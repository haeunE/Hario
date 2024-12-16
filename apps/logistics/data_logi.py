import pandas as pd


file_paths = [
    'apps/logistics/logi_before.csv',
    'apps/logistics/logi_during.csv',
    'apps/logistics/logi_after.csv'
]

dfs = [pd.read_csv(file, encoding='euc-kr') for file in file_paths]

all_df = pd.concat(dfs)
grouped_df = all_df.groupby(['배송년월일']).sum()
grouped_df.to_csv('apps/logistics/logi_all.csv')

# file_path = 'apps/logistics/logi_address_seoul.csv'
# df = pd.read_csv(file_path, encoding='euc-kr')
# df_cleaned = df.drop_duplicates(subset=['주소'], keep='first', )
# df_cleaned.to_csv('logi_add_seoul.csv', index=False)