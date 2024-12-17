import pandas as pd
import numpy as np

# 전세계 코로나 생존자
path = 'apps/graph/static/DAY_COVID_ALL.csv'
covid_all = pd.read_csv(path)
path = 'apps/graph/static/DAY_COVID_ALL2.csv'
covid_all2 = pd.read_csv(path)
# 한국 코로나 데이터(한글 수정)
path = 'apps/graph/static/DAY_COVID_K.csv'
k_covid = pd.read_csv(path, encoding='euc-kr')

covid_all2.drop(columns=['Column203'], inplace=True)

#================================ covid_all 전처리 ================================
# covid_all을 복제하여 새로운 Datarame 생성
covid_all_copy = covid_all2.copy()
# '날짜' 열을 인덱스로 설정
covid_all_copy.set_index('날짜', inplace=True)
# 모든 값이 0인 행을 찾아 삭제
covid_all_copy = covid_all_copy.loc[~(covid_all_copy == 0).all(axis=1)]

#============================== covid 전처리 ======================================


# 완치자수 한국 데이터만 추출
covid_save_korea = covid_all_copy['Korea, South']
# 모두 0인 행 지우기
covid_save_korea = covid_save_korea[covid_save_korea != 0]
covid_save_korea = covid_save_korea.reset_index()
covid_save_korea['날짜'] = pd.to_datetime(covid_save_korea['날짜'])
covid_save_korea['날짜'] = covid_save_korea['날짜'].dt.strftime('%Y-%m-%d')
# covid_save_korea.drop(columns=['level_0', 'index'], inplace=True)

# 한국 코로나데이터와 한국 코로나 완치자수 데이터 병합
# k_covid.drop(columns=['Unnamed: 0'], inplace=True)
merged_covid = pd.merge(k_covid, covid_save_korea, on='날짜', how='left')
merged_covid['Korea, South'] = merged_covid['Korea, South'].fillna(0)
merged_covid.rename(columns={'Korea, South': '완치자수'}, inplace=True)
merged_covid['완치자수'] = merged_covid['완치자수'].astype(int)

day_covid = merged_covid.set_index('날짜').T
day_covid.index.name = '집계'

melted_data = day_covid.reset_index().melt(id_vars='집계', var_name='날짜', value_name='값')


# 날짜를 datetime 형식으로 변환
merged_covid['날짜'] = pd.to_datetime(merged_covid['날짜'])

# '년월' 컬럼 생성 (연도-월, 문자열 형식으로 변환)
merged_covid['년월'] = merged_covid['날짜'].dt.to_period('M').astype(str)

# 사망자수 컬럼에 대한 이전 날짜와의 차이 계산
merged_covid['사망자수_차이'] = merged_covid['사망자수'].diff()
merged_covid['완치자수_차이'] = merged_covid['완치자수'].diff()
merged_covid['확진자수_차이'] = merged_covid['확진자수'].diff()
merged_covid['검사수_차이'] = merged_covid['누적검사'].diff()

# ==================== covid_monthly : 전월대비 퍼센트 데이터프레임 ===================
covid_monthly = merged_covid.groupby('년월').agg({
    '사망자수_차이': 'sum',
    '완치자수_차이': 'sum',
    '확진자수_차이' : 'sum',
    '검사수_차이' : 'sum'
}).reset_index()

# 전월대비 퍼센트 계산
covid_monthly['사망자수차이_전월대비'] = covid_monthly['사망자수_차이'].pct_change().mul(100).round(2)
covid_monthly['완치자수차이_전월대비'] = covid_monthly['완치자수_차이'].pct_change().mul(100).round(2)

