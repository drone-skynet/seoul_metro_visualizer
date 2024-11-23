# frontend.py

# 사용하지 않는 변수에 대한 pylint 경고를 무시
# pylint: disable=unused-variable 
# 문자열에서 비정상적인 백슬래시 pylint 경고를 무시
# pylint: disable=anomalous-backslash-in-string  

import generic
import pandas as pd
import numpy as np
from datetime import datetime
import math
import time
import altair as alt # 데이터 시각화 라이브러리
import pydeck as pdk # 지도 시각화 라이브러리
import streamlit as st

# Streamlit 사이드바를 표시하는 함수 (날짜 범위 선택 UI)
def display_sidebar(data):
    min_date, max_date = None, None
    st.sidebar.header('아래에서 옵션을 선택하세요') # 사이드바 헤더

    # 최소 / 최대 날짜 선택
    st.sidebar.markdown('날짜를 선택하세요')
    date_ranges = data['Date'].str[:7].unique().tolist() # 날짜 데이터를 월 단위로 추출
    min_date = st.sidebar.selectbox('시작 날짜', date_ranges) # 시작 날짜 선택
    date_ranges = [date for date in date_ranges if date >= min_date]
    max_date = st.sidebar.selectbox('종료 날짜', date_ranges) # 종료 날짜 선택

    # 사용자가 선택한 시작 날짜, 종료 날짜
    return min_date, max_date

# 지도 애니메이션(pydeck)을 실행하는 함수
def animate_maps(data, color_set, min_date, max_date):
    if min_date == max_date:
        st.subheader(f'{min_date} 지하철 이용 현황')
    else:
        st.subheader(f'{min_date} 부터 {max_date} 까지의 지하철 이용 현황')
    st.write('노선 색상: 지하철 노선의 색상')
    st.write('원 크기: 이용자 수')

    # 선택된 날짜 범위로 데이터 필터링
    data = data.drop(data.loc[(data['Date'].str[:7] < min_date) | (data['Date'].str[:7] > max_date)].index)

    # Hex 색상을 RGB로 변환하는 내부 함수
    def hex_to_rgb(hex):
        hex = hex.lstrip('#')
        return list(int(hex[i:i+2], 16) for i in (0, 2, 4))

    # 데이터에 색상, 이용자 수, 크기 열 추가
    data.loc[:, 'color'] = data['color'].apply(hex_to_rgb)
    data.loc[:, 'users'] = (data.loc[:, 'EntriesN'] + data.loc[:, 'ExitsN'])
    data.loc[:, 'size'] = data.loc[:, 'users'] / data.loc[:, 'users'].max()

    date_ranges = list(data['Date'].unique()) # 고유한 날짜 리스트 생성
    current_date = st.markdown('현재 날짜: ') # 현재 날짜 표시
    map = st.empty() # 지도 공간 생성

    # 날짜별로 지도 업데이트
    for idx, date in enumerate(date_ranges):
        current_date.markdown(f"현재 날짜: {date}")
        r = show_map(data.loc[data['Date'] == date]) # 날짜별 데이터로 지도 생성
        time.sleep(0.2) # 지도 갱신 간격
        map.pydeck_chart(r, use_container_width=True) # 업데이트된 지도 표시

# pydeck 지도를 생성하는 함수 (특정 날짜의 지하철 이용 데이터를 지도에 시각화)
def show_map(data):
    # 지도 초기 뷰 설정
    view_state = pdk.ViewState(
        latitude=data['Latitude'].mean(),
        longitude=data['Longitude'].mean(),
        zoom=9
    )

    # pydeck의 ScatterplotLayer 설정
    scatterplotlayer = pdk.Layer(
        "ScatterplotLayer",
        data=data,
        pickable=True,
        opacity=0.6,
        auto_highlight=True,
        filled=True,
        radius_scale=2500,
        radius_min_pixels=3,
        radius_max_pixels=100,
        get_fill_color='color',
        get_position='[Longitude,Latitude]',
        get_radius='size',
    )

    # 지도에 표시될 툴팁 설정
    tooltip = {
        "html": "<b>노선:</b> {Line} <br /><b>역명:</b> {Station} <br /><b>탑승 인원:</b> {EntriesN} <br /><b>하차 인원:</b> {ExitsN}"
    }

    # pydeck 객체 생성
    r = pdk.Deck(
        layers=[scatterplotlayer],
        initial_view_state=view_state,
        map_style=pdk.map_styles.LIGHT,
        tooltip=tooltip,
    )

    return r



# # altair를 사용해 다양한 차트를 생성하는 함수
# """
# 주요 역할:
# 1. 고용 강점(Employment Strengths) 산포도 표시
# 2. 물가 지수(Price Index) 스택형 막대 차트 표시
# 3. 가격 책정력(Pricing Power) 막대 차트 표시
# """
# def show_chart(data, items):
#     # 데이터 열(컬럼) 및 제목 설정
#     stat = {
#         'rank': 'Rank',
#         'All Employees': 'All Employees (1K)',
#         'Avg Hourly Wages': 'Avg Hourly Wages',
#         'eWage': 'Pricing Power',
#         'score': 'Employment Strengths',
#         'eCPI': 'Price Index'
#     }

#     # 키와 값 리스트 생성
#     stat_text = list(stat.values()) # 그래프 축 또는 툴팁에 사용할 텍스트
#     stat_keys = list(stat.keys()) # 데이터 열 이름

#     # 선택된 데이터 항목 필터링
#     items = [key for key, value in items.items() if value != 0]

#     # 필요한 데이터 열만 필터링
#     data = data[['year', 'cbsa_area', 'Metro area'] + stat_keys + items]

#     # 고용 강점 산포도(Subheader)
#     st.subheader('Employment strengths')

#     # 고용 강점(Employment Strengths) 산포도 차트 생성
#     scatter = (
#         alt.Chart(data)
#         .mark_circle()
#         .encode(
#             x=alt.X(stat_keys[1], title=stat_text[1]), # X축: 전체 고용자 수
#             y=alt.Y(stat_keys[2], title=stat_text[2]), # Y축: 평균 시간당 임금
#             size=alt.Size(stat_keys[4], legend=None), # 원 크기: 고용 강점
#             tooltip=[
#                 alt.Tooltip('Metro area'),
#                 alt.Tooltip(stat_keys[0], title=stat_text[0]),
#                 alt.Tooltip(stat_keys[1], title=stat_text[1]),
#                 alt.Tooltip(stat_keys[2], title=stat_text[2], format='$')
#             ]
#         )
#     )
#     st.altair_chart(scatter, use_container_width=True) # Streamlit에 차트 출력

#     # 물가 지수 섹션
#     st.subheader('Price Index')

#     # 물가 지수(Price Index) 스택형 막대 차트 생성
#     stacked_cpi = (
#         alt.Chart(data)
#         .transform_fold(items, ['Item', 'Price Index']) # 데이터 변환
#         .mark_bar()
#         .encode(
#             x=alt.X('Price Index:Q'), # X축: 물가 지수 값
#             y=alt.Y('Metro area:N', sort=alt.EncodingSortField(field=stat_keys[5], order='descending')), # Y축: 대도시 이름
#             color=alt.Color('Item:N'), # 색상: 선택된 항목
#             tooltip=[
#                 alt.Tooltip('Metro area'),
#                 alt.Tooltip('Item:N'),
#                 alt.Tooltip('Price Index:Q'),
#                 alt.Tooltip(stat_keys[5], title=stat_text[5])
#             ]
#         )
#     )
#     st.altair_chart(stacked_cpi, use_container_width=True) # Streamlit에 차트 출력

#     # 가격 책정력 섹션
#     st.subheader('Pricing Power')

#     # 가격 책정력(Pricing Power) 막대 차트 생성
#     stacked_pp = (
#         alt.Chart(data)
#         .mark_bar()
#         .encode(
#             x=alt.X(stat_keys[3], title=stat_text[3]), # X축: 가격 책정력
#             y=alt.Y('Metro area:N', sort=alt.EncodingSortField(field=stat_keys[3], order='descending')), # Y축: 대도시 이름
#             tooltip=[
#                 alt.Tooltip('Metro area'),
#                 alt.Tooltip(stat_keys[2], title=stat_text[2]),
#                 alt.Tooltip(stat_keys[5], title=stat_text[5]),
#                 alt.Tooltip(stat_keys[3], title=stat_text[3])
#             ]
#         )
#     )
#     st.altair_chart(stacked_pp, use_container_width=True) # Streamlit에 차트 출력
