import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import numpy as np
from preprocess.pre_stock import data
from preprocess.pre_stock import company_colors


# # Sample 데이터 준비
# data = pd.DataFrame({
#     'Date': pd.date_range(start='2020-01-01', end='2023-12-31', freq='D'),
#     'Name': ['CJ제일제당', 'CJ ENM', 'CJ대한통운'] * 365,
#     'Close': abs(100 + 20 * pd.np.random.randn(365 * 3)),
#     'Open': abs(100 + 15 * pd.np.random.randn(365 * 3)),
#     'High': abs(110 + 25 * pd.np.random.randn(365 * 3)),
#     'Low': abs(90 + 10 * pd.np.random.randn(365 * 3)),
# })

# # Date 컬럼 변환
# data['Date'] = pd.to_datetime(data['Date'])

# Dash 앱 초기화
app = dash.Dash(__name__)

# 앱 레이아웃 설정
app.layout = html.Div([
    html.H1("CJ Stock Price Distribution", style={'textAlign': 'center'}),
    
    # 드롭다운: 계열사 선택
    html.Div([
        html.Label("Select Affiliate:"),
        dcc.Dropdown(
            id='affiliate-dropdown',
            options=[{'label': name, 'value': name} for name in data['Name'].unique()],
            value=data['Name'].unique()[0],  # 기본 선택
            multi=False
        ),
    ], style={'width': '48%', 'display': 'inline-block'}),
    
    # 드롭다운: 연도 선택
    html.Div([
        html.Label("Select Year:"),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': year, 'value': year} for year in data['Date'].dt.year.unique()],
            value=data['Date'].dt.year.unique()[0],  # 기본 선택
            multi=False
        ),
    ], style={'width': '48%', 'display': 'inline-block'}),
    
    # 그래프 출력
    dcc.Graph(id='price-boxplot'),
])

# 콜백 함수: 드롭다운 선택에 따른 그래프 업데이트
@app.callback(
    Output('price-boxplot', 'figure'),
    [Input('affiliate-dropdown', 'value'),
     Input('year-dropdown', 'value')]
)
def update_graph(selected_affiliate, selected_year):
    # 데이터 필터링
    filtered_data = data[
        (data['Name'] == selected_affiliate) & 
        (data['Date'].dt.year == selected_year)
    ]
    
    # 데이터 "긴 형식"으로 변환
    melted_data = filtered_data.melt(
        id_vars=['Date', 'Name'], 
        value_vars=['Close', 'Open', 'High', 'Low'], 
        var_name='Price_Type', 
        value_name='Price'
    )
    
    # 그래프 생성
    fig = px.box(
        melted_data,
        x='Date', 
        y='Price', 
        color='Name',  # Name을 기준으로 색상 매핑
        color_discrete_map=company_colors,  # 색상 사전 전달
        title=f'Price Distribution of {selected_affiliate} in {selected_year}',
        labels={'Price': 'Stock Price', 'Date': 'Trading Date'}
    )
    # x축 눈금 포맷 설정
    fig.update_layout(
        xaxis=dict(
            tickformat="%b %Y",  # 월 이름과 연도 표시 (예: Jan 2020)
            tickmode="linear",   # 선형 눈금
            dtick="M1"           # 한 달 간격으로 눈금 표시
        )
    )
    return fig

# 앱 실행
if __name__ == '__main__':
    app.run_server(debug=True)
