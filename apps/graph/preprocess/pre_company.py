import pandas as pd
import numpy as np

file_path = 'apps/graph/static/account_affiliate.xlsx'
data = pd.read_excel(file_path, sheet_name=None)

FW = data['CJ프레시웨이']
CJ = data['제일제당']
SD = data['스튜디오드래곤']
BS = data['CJ바이오사이언스']
DT = data['대한통운']
ENM = data['ENM']
SF = data['CJ씨푸드']
CGV = data['CGV']
# 데이터 확인
print("CJ프레시웨이 데이터:")
print(FW.head())

company_code = {
    'FW' : 'CJ프레시웨이',
    'CJ' : '제일제당',
    'SD' : '스튜디오드래곤',
    'BS' : 'CJ바이오사이언스',
    'DT' : '대한통운',
    'ENM' : 'ENM',
    'SF' : 'CJ씨푸드',
    'CGV' : 'CGV'
}
# 색상 팔레트 설정 (회사별 색상을 구분하기 위해)
company_colors = {
    '제일제당': 'Lightsalmon',
    '스튜디오드래곤':'Pink',
    '대한통운':'Royalblue',
    'ENM':'Plum',
    'CJ프레시웨이':'Lightcoral',
    'CJ씨푸드':'Powderblue',
    'CGV': 'Khaki',
    'CJ바이오사이언스' : 'Yellowgreen'
}

    # 'company_code'와 'globals()'를 사용하여 각 회사의 매출액 데이터프레임을 결합
all_sales = pd.DataFrame()

for code, name in company_code.items():
    company_data = globals()[code]  # 회사 데이터프레임을 변수명으로 참조
    company_data_filtered = company_data[company_data["분기"].dt.month != 12].copy()  # 12월 제외

    
    # 회사명 추가
    company_data_filtered["회사명"] = name
    
    # 매출액 데이터를 결합
    all_sales = pd.concat([all_sales, company_data_filtered])

all_sales['매출액'] = all_sales['매출액'].replace(0, np.nan)
all_sales['당기순이익'] = all_sales['당기순이익'].replace(0, np.nan)
all_sales['영업이익'] = all_sales['영업이익'].replace(0, np.nan)
all_sales['성장률'] = all_sales.groupby('회사명')['매출액'].pct_change() * 100
quarter_map = {3: 'Q1', 6: 'Q2', 9: 'Q3'}
all_sales['분기Q'] = all_sales['월'].map(quarter_map)


