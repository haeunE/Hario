import pandas as pd
import numpy as np
from datetime import datetime


# 계열사별 일일 주식 데이터(종가, 시가, 최고가, 최소가)
path = 'apps/graph/static/cj_stocks_prices.csv'
cj_day_stock = pd.read_csv(path)


company_colors2 = {
    'CJ제일제당': 'Lightsalmon',
    '스튜디오드래곤':'Pink',
    'CJ대한통운':'Royalblue',
    'CJ ENM':'Plum',
    'CJ프레시웨이':'Lightcoral',
    'CJ씨푸드':'Powderblue',
    'CJ CGV': 'Khaki',
    'CJ바이오사이언스' : 'Yellowgreen'
}

#====================== 전처리 =============================
cj_day_stock.rename(columns={'Stock Name': 'Name'}, inplace=True)
cj_day_stock['Date'] = pd.to_datetime(cj_day_stock['Date'], format='%Y%m%d')
cj_day_stock = cj_day_stock.sort_values(by='Date')

# data['Date'] = data['Date'].astype(str)  # Date를 문자열로 변환
# 2020년 데이터만 필터링
# filtered_data = data.query('Date.str.startswith("2020")', engine='python')

# Time 컬럼을 datetime.time 형식으로 변환
# cj_live_stock['Time'] = cj_live_stock['Time'].astype(str).str.zfill(6)
# cj_live_stock['Time'] = cj_live_stock['Time'].apply(lambda x: datetime.strptime(x, '%H%M%S').time())
# cj_live_stock = cj_live_stock.sort_values(by='Time').reset_index(drop=True)