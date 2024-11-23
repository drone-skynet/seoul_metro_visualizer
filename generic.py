# generic.py: 데이터 로딩 및 전처리

# 사용하지 않는 변수에 대한 pylint 경고를 무시
# pylint: disable=unused-variable 
# 문자열에서 비정상적인 백슬래시 pylint 경고를 무시
# pylint: disable=anomalous-backslash-in-string 

import numpy as np
import pandas as pd
from datetime import datetime
import streamlit as st

# 데이터를 읽고 전처리한 후 병합하는 함수
def preprocess(filepath, typelist, line_mapping, color_set):
    # 원시 데이터와 지도 데이터를 읽고 복사
    raw = read_dataset(filepath, typelist[0]).copy()
    map = read_dataset(filepath, typelist[1]).copy()

    # 데이터 정리
    raw = clean_dataset('raw', raw, color_set, line_mapping)
    map = clean_dataset('map', map, color_set)

    # 데이터 병합
    data = merge_dataset(raw, map)
    return data

# Streamlit 캐시를 사용해 데이터 로드 성능을 최적화하며, 데이터 파일을 읽어들이는 함수
@st.cache_data  
def read_dataset(filepath, filelist):
    if type(filelist) == list: # 파일 리스트인 경우 각 파일을 읽고 병합
        for idx, filename in enumerate(filelist):
            ds = pd.read_csv(filepath + filename)
            # 마지막 열 제거 후 열 이름 지정
            ds = ds.iloc[:, :-1]
            ds.columns = ['Date', 'Line', 'Station', 'EntriesN', 'ExitsN']

            # 날짜 형식을 변환
            ds['Date'] = ds['Date'].astype(str).apply(lambda x: x[:4] + '-' + x[4:6] + '-' + x[6:])

            # 역 이름에서 괄호 내용 제거
            ds['Station'] = ds['Station'].str.split('(', expand=True)[0]

            # 날짜 기준으로 정렬
            ds = ds.sort_values(by='Date')

            # 첫 번째 파일은 초기 데이터로 설정, 이후 데이터 병합
            if idx == 0:
                data = ds
            else:
                data = pd.concat([data, ds], axis=0)
    else: # 파일 리스트가 아닌 경우 단일 파일 읽기
        data = pd.read_csv(filepath + filelist)

    return data

# 데이터 정리 및 전처리 함수
def clean_dataset(type, data, color_set, line_mapping=None):
    if type == 'raw': # 원시 데이터 처리
        # 특정 역에 대해 노선 이름을 '경의/중앙선'으로 변경
        data.loc[
            (data['Station'].isin(['서빙고', '옥수', '왕십리', '응봉', '이촌', '청량리', '한남'])) & (data['Line'] == '경원선'),
            'Line'
        ] = '경의/중앙선'

        # 노선 이름을 매핑된 이름으로 대체
        for dest, src in line_mapping.items():
            data['Line'] = data['Line'].replace(src, dest)
    elif type == 'map': # 지도 데이터 처리
        # 역과 노선을 기준으로 평균 위도와 경도를 계산
        data = data.groupby(['Station', 'Line'])[['Latitude', 'Longitude']].mean().reset_index()

        # 노선별 색상 추가
        data['color'] = data['Line'].apply(lambda x: color_set.get(x))
        
        # NaN 값 제거
        data.dropna(inplace=True)

    return data

# 두 데이터 프레임을 병합하는 함수
def merge_dataset(raw_data, map_data):
    return pd.merge(raw_data, map_data, how='inner', on=['Station', 'Line'])
