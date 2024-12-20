import pandas as pd
import matplotlib
matplotlib.use('Agg')

# 엑셀 파일 선처리 작업

file_paths = [
    'apps/logistics/logi_before.csv',
    'apps/logistics/logi_during.csv',
    'apps/logistics/logi_after.csv'
]

# 불필요한 열 제거
column_remove = [
    '송하인_시명', '송하인_시코드', '송하인_구명', '송하인_구코드',
    '수하인_시명', '수하인_시코드', '수하인_구명', '수하인_구코드'
]

# CSV 파일들을 읽고, 모든 값이 0인 행을 제외
dfs = []
for file in file_paths:
    df = pd.read_csv(file, encoding='euc-kr')
    zerox = df.loc[(df != 0).any(axis=1)]  # 값이 0이 아닌 행만
    dfs.append(zerox)

df_all = pd.concat(dfs)

# 필요한 열만 남겨두고 날짜별 운송량 집계
df_cleaned = df_all.drop(columns=column_remove)
grouped_df = df_cleaned.groupby(['배송년월일']).sum()

grouped_df.to_csv('apps/logistics/logi_all.csv', encoding='utf-8-sig')

