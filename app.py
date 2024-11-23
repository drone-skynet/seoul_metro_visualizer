# app.py: SeoulMetro 시각화를 위한 Streamlit 애플리케이션 실행 파일

# 사용하지 않는 변수에 대한 pylint 경고를 무시
# pylint: disable=unused-variable 
# 문자열에서 비정상적인 백슬래시 pylint 경고를 무시
# pylint: disable=anomalous-backslash-in-string 

"""
종속성(Dependencies):
데이터 - geojson (위도와 경도 정보 포함)

모듈(modules):
frontend.py - 프론트엔드 작업
generic.py - 일일 통계와 지도 데이터를 로드
"""

import streamlit as st
import pandas as pd
import generic
import frontend
import pydeck as pdk
import math

# 데이터 파일 경로 설정
file_path = {'data':'data/SeoulMetro_'}  
# file_list = {'map':'Stations.csv','raw':['202004.csv','202005.csv']}
file_list = {'map':'Stations.csv','raw':['202004.csv','202005.csv','202006.csv','202007.csv','202008.csv','202009.csv']} # 지도 및 원시 데이터 파일 설정

line_mapping = { # 지하철 노선 맵핑
    '1호선':['1호선','경원선', '경인선', '경부선', '장항선'],
    '3호선':['3호선','일산선'],
    '4호선':['4호선','안산선','과천선'],
    '9호선':['9호선','9호선2~3단계'],
    '수인/분당선':['수인선','분당선'],
    '경의/중앙선':['경의선','중앙선'],
    '공항철도':['공항철도 1호선']
}

color_set = { # 지하철 노선별 색상 설정
    '1호선':'#0052A4', '2호선':'#009D3E', '3호선':'#EF7C1C',
    '4호선':'#00A5DE', '5호선':'#996CAC', '6호선':'#CD7C2F',
    '7호선':'#747F00', '8호선':'#EA545D', '9호선':'#A17E46',
    '수인/분당선':'#F5A200', '우이신설선':'#B0CE18', '공항철도':'#0090D2'
}

# 헤더 섹션
st.title('서울 수도권 지하철 이용 현황') # 제목 설정
update_status = st.markdown("원시 데이터를 불러오는 중...") # 사이드바에 표시될 데이터의 사전 로드 상태 업데이트

# 데이터 전처리
data = generic.preprocess(file_path['data'], [file_list['raw'], file_list['map']], line_mapping, color_set)
update_status.markdown('데이터 로드 완료!')

# 사이드바 섹션 (주요 섹터, 지역 및 연도 선택)
min_date, max_date = frontend.display_sidebar(data) # 사용자 선택값을 반환

# 메인 섹션
# # 차트 표시
# weights = [] # `weights` 정의 필요 (없다면 빈 리스트로 초기화)
# sel_focus = [0] # 선택된 항목 (예시로 첫 번째 항목 선택)
# frontend.show_chart(data, weights[int(sel_focus[0])]) # 차트 표시

# 지도 표시
frontend.animate_maps(data, color_set, min_date, max_date) # pydeck 애니메이션 지도 표시

# 하단의 크레딧 섹션
st.subheader('출처')
data_source = '서울 열린데이터 광장(https://data.seoul.go.kr)'
st.write('데이터 출처: ' + data_source)
st.write('지도 제공: Mapbox, OpenStreetMap')
