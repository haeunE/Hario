import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

file_path = 'apps/graphtest/static/account_affiliate.xlsx'
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

# Dash 애플리케이션 초기화
graphtest = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# 'company_code'와 'globals()'를 사용하여 각 회사의 매출액 데이터프레임을 결합
all_sales = pd.DataFrame()

for code, name in company_code.items():
    company_data = globals()[code]  # 회사 데이터프레임을 변수명으로 참조
    company_data_filtered = company_data[company_data["분기"].dt.month != 12].copy()  # 12월 제외

    
    # 회사명 추가
    company_data_filtered["회사명"] = name
    
    # 매출액 데이터를 결합
    all_sales = pd.concat([all_sales, company_data_filtered])

# Plotly Express를 사용하여 시각화 생성
take_fig = px.scatter(all_sales, x='분기', y='매출액', color='회사명', title='회사별 매출액', trendline="lowess", trendline_options=dict(frac=0.35))

# affiliate_count_fig = px.bar(all_sales, x='회사', y='Count', title='회사별 카운트', color='회사', text='Count', orientation='h')

# Dash 레이아웃 설정
graphtest.layout = html.Div([
    # 드롭다운 메뉴 (회사 선택)
    dcc.Dropdown(
        id='company-dropdown',
        options=[
            {'label': name, 'value': name} for name in company_code.values()
        ] + [{'label': '모두 선택', 'value': '모두 선택'}],
        value='CJ프레시웨이',  # 기본값 설정
        multi=False,
        style={'width': '50%', 'margin': 'auto'}
    ),
    
    # 그래프 영역
    dcc.Graph(id='sales-graph', figure=take_fig)
])

# 콜백을 통해 드롭다운 선택에 따라 그래프를 업데이트
@graphtest.callback(
    dash.dependencies.Output('sales-graph', 'figure'),
    [dash.dependencies.Input('company-dropdown', 'value')]
)
def update_graph(selected_company):
    if selected_company == '모두 선택':
        filtered_data = all_sales  # 모든 데이터 사용
    else:
        # 선택된 회사 필터링
        filtered_data = all_sales[all_sales['회사명'] == selected_company]
    
    # Plotly Express로 그래프 업데이트
    fig = px.scatter(filtered_data, x='분기', y='매출액', color='회사명', title=f'{selected_company}의 매출액', trendline="lowess", trendline_options=dict(frac=0.35))
    return fig

def register_dash(graphtest):
    graphtest.title = 'Graph Dashboard'
    graphtest.layout = graphtest.layout  # Dash layout을 Flask 블루프린트로 등록
