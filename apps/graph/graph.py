import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from apps.graph.preprocess.pre_covid import covid_monthly
from apps.graph.preprocess.pre_company import all_sales,company_colors,company_data,company_code
from apps.graph.preprocess.pre_stock import cj_day_stock,company_colors2
from apps.graph.preprocess.save_graph import save_sessionfig
from apps.graph.preprocess.live_stock import connect
from apps.graph.preprocess.now_stock import now_stock
import plotly.io as pio
import time
import asyncio
import io
import json
from datetime import datetime



def company_dash(app):

    # Dash 애플리케이션 초기화
    graph = dash.Dash(__name__, server=app, url_base_pathname='/graph/company/', external_stylesheets=[dbc.themes.BOOTSTRAP])
    # graph.enable_dev_tools(debug=True)
    r, g, b = 255, 0, 0  # 빨간색
    # Plotly Express를 사용하여 시각화 생성
    # take_fig = px.scatter( all_sales[all_sales['회사명'] == 'CJ프레시웨이'], x='분기', y='매출액', color='회사명', title='회사별 매출액', trendline="lowess", trendline_options=dict(frac=0.35), marginal_y="histogram")
    take_fig = px.scatter(
        all_sales[all_sales['회사명'] == 'CJ프레시웨이'], 
        x='분기', 
        y='매출액', 
        color='회사명', 
        title='회사별 매출액', 
        trendline="lowess", 
        trendline_options=dict(frac=0.15), 
        marginal_y="histogram",
        color_discrete_map=company_colors  # 색상 매핑
    )
    

    profit_fig = go.Figure()

    # 색상 설정
    color = company_colors.get('CJ프레시웨이', 'black')

    # 당기순이익 (점선)
    profit_fig.add_trace(go.Scatter(
        x=company_data['분기'],
        y=company_data['당기순이익'],
        mode='lines+markers',
        name='CJ프레시웨이',
        legendgroup='CJ프레시웨이',
        showlegend=False,
        line=dict(dash='dot', color=color, width=2),
        marker=dict(symbol='circle', size=10)
    ))

    # 영업이익 (실선)
    profit_fig.add_trace(go.Scatter(
        x=company_data['분기'],
        y=company_data['영업이익'],
        mode='lines+markers',
        name=f'CJ프레시웨이 영업이익',
        legendgroup='CJ프레시웨이',
        showlegend=False,  # 범례 숨기기
        line=dict(dash='solid', color=color, width=2),
        marker=dict(symbol='square', size=10)
    ))
    # '사망자수_차이' 추가 (보조 y축 사용)
    profit_fig.add_trace(go.Scatter(
        x=covid_monthly['년월'],
        y=covid_monthly['사망자수_차이'],
        mode='lines',
        name='사망자수 차이',  # 레이블
        line=dict(dash='solid', color=f'rgba({r}, {g}, {b}, 0.5)', width=2),  # 선 색상 설정
        # marker=dict(color='blue', size=8),  # 마커 색상 설정
        yaxis='y2'  # 보조 y축으로 설정
    ))

    # 그래프 레이아웃 설정
    profit_fig.update_layout(
        title=f'CJ프레시웨이의 영업이익과 당기순이익 ( ㅡ : 영업이익 | -- : 당기순이익 )',
        xaxis_title='분기',
        yaxis_title='이익 (원)',
        template='plotly_white',
        legend_title='회사명',
        yaxis2=dict(
            title='사망자수 차이',  # 보조 y축 제목
            overlaying='y',  # 기본 y축과 겹치도록 설정
            side='right'  # 보조 y축을 오른쪽에 표시
        )
    )
    # affiliate_count_fig = px.bar(all_sales, x='회사', y='Count', title='회사별 카운트', color='회사', text='Count', orientation='h')


    growth_all_fig = px.bar(
        all_sales,
        x='성장률',
        y='회사명',
        color='회사명',
        orientation='h',
        title='회사별 10년간 성장률 격차(%)',
        color_discrete_map=company_colors
    )

    growth_all_fig.update_layout(
        xaxis_title='성장률 (%)',
        yaxis_title='회사명',
        template='plotly_white',
        legend_title='회사명'
    )
    # 수직선 추가하기
    growth_all_fig.add_vline(x=0,line_width=2, line_dash="dash",
                line_color="#C2151B",
                annotation_text="0", 
                annotation_position="top left",
                annotation_font_size=10,
                annotation_font_color="#C2151B",
                annotation_font_family="Times New Roman")

    growth_fig = px.violin(
        all_sales[all_sales['회사명'] == 'CJ프레시웨이'],  
        x='분기Q', 
        y='성장률', 
        color='회사명', 
        title='분기별 성장률(%)',
        box=True,  # 박스 표시
        points='all',  # 모든 포인트 표시
        color_discrete_map=company_colors
    )


    # Dash 레이아웃 설정
    graph.layout = html.Div([
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
        dcc.Graph(id='sales-graph', figure=take_fig),

        # 두 번째 그래프: `go.Figure` 기반 그래프
        dcc.Graph(id='profit-graph', figure=profit_fig), 

        #성장률
        dcc.Graph(id='growth-all-graph', figure=growth_all_fig),

        #계열사별 성장률
        dcc.Graph(id='growth-graph', figure=growth_fig)

    ])

    # 콜백을 통해 드롭다운 선택에 따라 그래프를 업데이트
    @graph.callback(
        [dash.dependencies.Output('sales-graph', 'figure'),dash.dependencies.Output('profit-graph','figure'),dash.dependencies.Output('growth-graph','figure')],
        [dash.dependencies.Input('company-dropdown', 'value')],
        prevent_initial_call=False
    )
    def update_graph(selected_company):
        print(selected_company)
        if not selected_company or selected_company == '모두 선택':
            filtered_data = all_sales  # 모든 데이터 사용
        else:
            # 선택된 회사 필터링
            filtered_data = all_sales[all_sales['회사명'] == selected_company]
        
        # Plotly Express로 그래프 업데이트
        # fig = px.scatter(filtered_data, x='분기', y='매출액', color='회사명', title=f'{selected_company}의 매출액', trendline="lowess", trendline_options=dict(frac=0.35), marginal_y="histogram")
        take_fig = px.scatter(
            filtered_data, 
            x='분기', 
            y='매출액', 
            color='회사명', 
            title=f'{selected_company}의 매출액', 
            trendline="lowess", 
            trendline_options=dict(frac=0.15), 
            marginal_y="histogram",
            color_discrete_map=company_colors  # 색상 매핑
        )

        profit_fig = go.Figure()

        # 회사별 데이터 추가
        for company_name in filtered_data['회사명'].unique():
            company_data = filtered_data[filtered_data['회사명'] == company_name]

            # 색상 설정
            color = company_colors.get(company_name, 'black')

            # 당기순이익 (점선)
            profit_fig.add_trace(go.Scatter(
                x=company_data['분기'],
                y=company_data['당기순이익'],
                mode='lines+markers',
                name=f'당기순이익',
                legendgroup=company_name,
                # showlegend=False,
                line=dict(dash='dot', color=color, width=2),
                marker=dict(symbol='circle', size=10)
            ))

            # 영업이익 (실선)
            profit_fig.add_trace(go.Scatter(
                x=company_data['분기'],
                y=company_data['영업이익'],
                mode='lines+markers',
                name=f'영업이익',
                legendgroup=company_name,
                # showlegend=False,  # 범례 숨기기
                line=dict(dash='solid', color=color, width=2),
                marker=dict(symbol='square', size=10)
            ))
        # '사망자수_차이' 추가 (보조 y축 사용)
        profit_fig.add_trace(go.Scatter(
            x=covid_monthly['년월'],
            y=covid_monthly['사망자수_차이'],
            mode='lines',
            name='사망자 발생(건)',  # 레이블
            line=dict(dash='solid', color=f'rgba({r}, {g}, {b}, 0.5)', width=2),  # 선 색상 설정
            # marker=dict(color='blue', size=8),  # 마커 색상 설정
            yaxis='y2'  # 보조 y축으로 설정
        ))

        # 그래프 레이아웃 설정
        profit_fig.update_layout(
            title=f'{selected_company}의 영업이익과 당기순이익 ( ㅡ : 영업이익 | -- : 당기순이익 )',
            xaxis_title='분기',
            yaxis_title='이익 (원)',
            template='plotly_white',
            legend=dict(
                title = "선",
                x=1.15,  # 범례를 그래프의 오른쪽에 위치시킴
                y=1,     # 범례의 수직 위치
                traceorder="normal",  # 범례 항목 순서
                font=dict(
                    family="Arial, sans-serif",
                    size=12,
                    color="black"
                ),
                borderwidth=1
            ),
            yaxis2=dict(
                title='사망자 발생(건)',  # 보조 y축 제목
                overlaying='y',  # 기본 y축과 겹치도록 설정
                side='right'  # 보조 y축을 오른쪽에 표시
            )
        )

        

        growth_fig = px.violin(
            filtered_data, 
            x='분기Q', 
            y='성장률', 
            color='회사명',
            color_discrete_map=company_colors, 
            title=f'{company_name}의 분기별 성장률(%)',
            box=True,  # 박스 표시
            points='all'  # 모든 포인트 표시
        )

        return take_fig, profit_fig, growth_fig
    
    return graph

def korea_covid(app):
    # 그래프 저장 함수 호출 (앱 실행 시 딱 한 번 실행)
    save_sessionfig()
    
    graph = dash.Dash(__name__, server=app,url_base_pathname='/graph/covid/', external_stylesheets=[dbc.themes.BOOTSTRAP])
    # limited_dates = day_covid['날짜'].unique()[::3]
    # Plotly 그래프
    # session_fig = px.bar(day_covid, title="한국 코로나 집계", color=day_covid.index, animation_frame="날짜", text_auto='.2s')
    # 저장된 그래프 로드
    session_fig = pio.read_json("apps/graph/static/session_fig.json")
    # 애니메이션 속도 조정

    monthly_fig = px.line(covid_monthly.loc[3:],x='년월', y=['사망자수차이_전월대비', '완치자수차이_전월대비'],markers=True)
    # 범례 이름을 원하는 대로 변경
    monthly_fig.for_each_trace(lambda t: t.update(name=t.name.replace('사망자수차이_전월대비', '전월대비 사망자수')
                                                .replace('완치자수차이_전월대비', '전월대비 완치자수')))
    monthly_fig.update_layout(
        xaxis_title='월별',
        yaxis_title='차이(%)'  # 그래프 스타일 (선택 사항)
    )
    monthly_fig.update_xaxes(ticks="outside", tickwidth=2, tickcolor='gray', ticklen=10)
    monthly_fig.update_yaxes(ticks="outside", tickwidth=2, tickcolor='gray', ticklen=10)

    # 레이아웃 구성
    graph.layout = html.Div([
        dbc.Container([
            # 첫 번째 그래프: 세션 별 코로나 집계
            html.H2("한국 코로나 집계", style={'textAlign': 'center', 'color': '#007bff', 'fontSize': '32px'}),
            html.Div(
                dcc.Graph(
                    id='covid-bar-chart',
                    figure=session_fig
                ), style={'padding': '30px'}
            ),
            # 두 번째 그래프: 월별 사망자수/완치자수 차이
            html.H2("월별 사망자수와 완치자수 차이", style={'textAlign': 'center', 'color': '#28a745', 'fontSize': '28px'}),
            html.Div(
                dcc.Graph(
                    id='monthly-line-chart',
                    figure=monthly_fig
                ), style={'padding': '30px'}
            ),
        ], fluid=True)
    ])
    return graph

def stock_dash(app):
    graph = dash.Dash(__name__, server=app,url_base_pathname='/graph/stock/', external_stylesheets=[dbc.themes.BOOTSTRAP])
    # 모든 회사 이름을 가져오기
    # 모든 회사 이름을 가져오기
    company_names = cj_day_stock['Name'].unique()
    
    # 앱 레이아웃 설정
    graph.layout = html.Div([
        html.H3("2018 ~ 2023 주가"),
        html.Br(),
        # 드롭다운 메뉴 (회사 선택)
        dcc.Dropdown(
            id='company-dropdown',
            options=[{'label': company, 'value': company} for company in company_names],
            value=company_names[0],  # 기본값은 첫 번째 회사
            style={'width': '50%'}
        ),
        html.Br(),
        # 날짜 범위 슬라이더
        dcc.RangeSlider(
            id='date-range-slider',
            min=cj_day_stock['Date'].min().year,
            max=cj_day_stock['Date'].max().year,
            step=1,
            marks={year: str(year) for year in range(cj_day_stock['Date'].min().year, cj_day_stock['Date'].max().year + 1)},
            value=[cj_day_stock['Date'].min().year, cj_day_stock['Date'].max().year],
            pushable=True
        ),
        
        # 그래프 출력 영역
        dcc.Graph(id='candlestick-graph'),
        dcc.Graph(id='bar-or-pie-graph'),
        dcc.Graph(id='trendline-graph')
    ])

    # 콜백 설정: 드롭다운 선택에 따른 캔들스틱 그래프 및 비율 그래프 업데이트
    @graph.callback(
        [Output('candlestick-graph', 'figure'),
         Output('bar-or-pie-graph', 'figure'),
         Output('trendline-graph', 'figure')],
        [Input('company-dropdown', 'value'),
         Input('date-range-slider', 'value')]
    )
    def update_graph(selected_company, selected_years):
        start_year, end_year = selected_years
        filtered_data = cj_day_stock[(cj_day_stock['Name'] == selected_company) &
                                     (cj_day_stock['Date'].dt.year >= start_year) &
                                     (cj_day_stock['Date'].dt.year <= end_year)]
        
        # 캔들스틱 차트 생성
        fig_candlestick = go.Figure(
            data=[go.Candlestick(
                x=filtered_data['Date'],
                open=filtered_data['Open'],
                high=filtered_data['High'],
                low=filtered_data['Low'],
                close=filtered_data['Close'],
                name=selected_company,
                increasing_line_color='red',
                decreasing_line_color='blue'
            )]
        )
        

        # 레이아웃 설정
        fig_candlestick.update_layout(
            title=f"{selected_company} 주가 그래프 ({start_year}-{end_year})",
            xaxis_title='Date',
            yaxis_title='당가',
            showlegend=False  # 범례 숨기기
        )

        # 상승 캔들과 하락 캔들 계산
        rising_candles = len(filtered_data[filtered_data['Close'] > filtered_data['Open']])
        falling_candles = len(filtered_data[filtered_data['Close'] < filtered_data['Open']])

        # 막대그래프 또는 파이차트 데이터 생성
        fig_type = 'pie'  # 예시: 막대그래프
        fig_bar_or_pie = px.pie(
            names=['Rising Candles', 'Falling Candles'],
            values=[rising_candles, falling_candles],
            title=f"증가 vs 하강 비율 ({start_year}-{end_year})"
        )
        
        # 그래프에 따라 막대그래프나 파이그래프를 설정
        if fig_type == 'bar':
            fig_bar_or_pie = go.Figure(
                data=[go.Bar(
                    x=['증가 Candles', '하강 Candles'],
                    y=[rising_candles, falling_candles],
                    marker=dict(color=['red', 'blue'])
                )]
            )
            fig_bar_or_pie.update_layout(
                title=f"증가 vs 하강 비율 ({start_year}-{end_year})",
                xaxis_title="Type",
                yaxis_title="Count"
            )

        # LOWESS 추세선 추가
        fig_lowess = px.scatter(
            filtered_data,
            x='Date',
            y='Close',
            color='Name',
            title=f'Daily Close Price of {selected_company} with LOWESS Trendline',
            trendline="lowess",  # LOWESS 추세선
            trendline_options=dict(frac=0.4),
            color_discrete_map=company_colors2  # 색상 맵 설정
        )

        # 롤링 추세선 추가
        fig_rolling = px.scatter(
            filtered_data,
            x='Date',
            y='Close',
            color='Name',
            trendline="rolling",  # 롤링 추세선
            trendline_options=dict(window=20),
            color_discrete_map=company_colors2  # 색상 맵 설정
        )

        # 새로운 데이터 객체를 생성하여 두 그래프의 데이터를 결합
        trendline_fig = go.Figure()

        # LOWESS 추세선 추가
        for trace in fig_lowess.data:
            if trace.mode == 'lines':
                trendline_fig.add_trace(trace)

        # 롤링 추세선 추가
        for trace in fig_rolling.data:
            if trace.mode == 'lines':
                trendline_fig.add_trace(trace)

        # 원본 데이터를 scatter로 추가
        for trace in fig_lowess.data:
            if trace.mode == 'markers':
                trendline_fig.add_trace(trace)

        # 레이아웃 업데이트
        trendline_fig.update_layout(
            title=f'{selected_company} 이동평균선 ({start_year}-{end_year})',
            xaxis_title='Date',
            yaxis_title='Close Price',
            showlegend=True
        )

        trendline_fig.data = [t for t in trendline_fig.data if t.mode == "lines"]
        trendline_fig.update_traces(showlegend=True)

        return fig_candlestick, fig_bar_or_pie, trendline_fig
    
    return graph

# def live_stock(app):
#     graph = dash.Dash(__name__, server=app,url_base_pathname='/graph/current/', external_stylesheets=[dbc.themes.BOOTSTRAP])
#     # # 초기 데이터
#     # initial_data = cj_live_stock
    

#     # # Figure 초기화
#     # live_stock_fig = px.line(initial_data, x='Time', y='Now')
#     # live_stock_fig.update_layout(yaxis_title="체결가 (원)")

#     # 레이아웃 설정
#     graph.layout = html.Div([
#         html.H1("실시간 주식 그래프"),
#         dcc.Graph(id='live-graph'),
#         dcc.Interval(
#             id='interval-component',
#             interval=10*1000,  # 1초마다 데이터를 업데이트
#             n_intervals=0
#         )
#     ])

#     # 그래프 업데이트 콜백 함수
#     @graph.callback(
#         Output('live-graph', 'figure'),
#         Input('interval-component', 'n_intervals')
#     )
#     def update_graph(n_intervals):
#         initial_data = cj_live_stock
#         try :
#             # 실시간 데이터 가져오기
#             stock_name = cj_live_stock['Stock Name'].iloc[0]  # Series가 아닌 첫 번째 값을 가져옴
#             new_data = asyncio.run(connect(stock_name))
#             print(new_data)
#         except Exception as e:
#             print('Fail Update!')
#             print(e)
#             print('Connect Again!')
#             time.sleep(0.1)

#             # 웹소켓 다시 시작
#             # 실시간 데이터 가져오기
#             new_data = asyncio.run(connect(cj_live_stock['Stock Name']))

#         # 데이터를 합쳐서 그래프 업데이트
#         updated_data = pd.concat([initial_data, new_data], ignore_index=True)

        
#         # 새로운 그래프 생성
#         live_stock_fig = px.line(updated_data, x='Time', y='Now')
#         live_stock_fig.update_layout(yaxis_title="체결가 (원)")

#         return live_stock_fig
#     return graph

def stock_live(app):
    # CJ 계열사 종목 코드
    cj_stocks = {
        "051500": "CJ프레시웨이",
        "097950": "CJ제일제당",
        "253450": "스튜디오드래곤",
        "311690": "CJ바이오사이언스",
        "000120": "CJ대한통운",
        "011150": "CJ씨푸드",
        "035760": "CJ ENM",
        "079160": "CJ CGV",
        "001040": "CJ(주)"
    }
    graph = dash.Dash(__name__, server=app, url_base_pathname='/graph/stocklive/', external_stylesheets=[dbc.themes.BOOTSTRAP])
    graph.layout = html.Div(
        style={
            "backgroundColor": "#f8f9fa",  # 배경색 설정 (여기서는 AliceBlue)
            "height": "auto",
        },
        children=[
        
            html.H3("실시간 주식 데이터 대시보드"),
            
            # 버튼 클릭 시 색상을 변경할 영역
            html.Div([
                html.Button(
                    f"{name} ({code})", 
                    id=f"btn-{code}", 
                    n_clicks=0, 
                    className="btn", 
                    style={
                        'margin': '5px',
                        'border': '2px solid',  # 테두리 색 지정 (파란색)
                        'borderRadius': '5px',  # 테두리 둥글게
                        'padding': '10px 20px',  # 버튼 패딩
                        'backgroundColor': '#E0DCDD',  # 배경 색 (흰색)
                        'color': '#3547B3',  # 글자 색 (파란색)
                        'fontWeight': 'bold'  # 글자 두껍게
                    }
                ) for code, name in cj_stocks.items()
            ], style={
                'display': 'flex',          # Flexbox 사용
                'gap': '10px',              # 버튼 간 간격
                'marginBottom': '20px',     # 아래 여백
                'flexWrap': 'wrap',         # 버튼이 줄 바꿈 되도록 설정
                'justifyContent': 'center', # 가로 방향 가운데 정렬
                'alignItems': 'center',     # 세로 방향 가운데 정렬
                'textAlign': 'center',      # 텍스트 가운데 정렬
            }),
            
            # 로딩 컴포넌트
            dcc.Loading(
                id="loading",
                type="circle",  # 스피너 모양
                style={
                    "backgroundColor": "#f8f9fa", 
                },
                children=[
                    # 그래프 컴포넌트
                    dcc.Graph(
                        id="live-graph",
                        style={
                        "backgroundColor": "#f8f9fa",
                        },
                    )
                ]
            ),
            
            dcc.Interval(
                id="interval-component",
                interval=30 * 1000,  # 30초마다 업데이트
                n_intervals=0,
            ),
            
            dcc.Store(id="selected-company", data=None),  # 선택된 회사 코드 저장
            dcc.Store(id="real-time-data", data=[]),  # 실시간 데이터 저장
        ]
    )

    @graph.callback(
        [Output("selected-company", "data"), Output("real-time-data", "data")],
        [Input(f"btn-{code}", "n_clicks") for code in cj_stocks] + [Input("interval-component", "n_intervals")],
        [State("selected-company", "data"), State("real-time-data", "data")],
        prevent_initial_call=False
    )
    def update_data(*args):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # 버튼 클릭 시 회사 코드 변경
        if button_id.startswith("btn-"):
            selected_code = button_id.split("-")[1]
            try:
                now_stock(selected_code)  # 회사 코드를 기반으로 CSV 생성
                path = 'apps/graph/static/cj_stocks_live.csv'
                cj_live_stock = pd.read_csv(path)
                cj_live_stock['Time'] = cj_live_stock['Time'].astype(str).str.zfill(6)
                cj_live_stock['Time'] = cj_live_stock['Time'].apply(lambda x: datetime.strptime(x, '%H%M%S').time())
                cj_live_stock = cj_live_stock.sort_values(by='Time').reset_index(drop=True)
                print("---------------------------------------------")
                print(cj_live_stock)
                update_data = cj_live_stock.to_json(orient='records')  # DataFrame
                print("update_data===========================")
                print(update_data)
            except Exception as e:
                print(f"Error generating CSV for {selected_code}: {e}")
                return dash.no_update, []  # 오류 발생 시 빈 데이터 반환
            return selected_code, update_data

        # 일정 시간 간격으로 실시간 데이터 업데이트
        selected_code = ctx.states.get("selected-company.data", None)
        print("+"*7)
        print(selected_code)
        if not selected_code:
            return dash.no_update, []

        try:
            # 기존 데이터 가져오기
            existing_data = ctx.states.get("real-time-data.data", [])
            print(type(existing_data)) 
            print("+"*50)
            if isinstance(existing_data, str):
                existing_data = json.loads(existing_data)
            print(existing_data)
            if existing_data:
                print(type(existing_data))
                existing_df = pd.DataFrame(existing_data)
            else:
                existing_df = pd.DataFrame(columns=columns)

            stock_name = cj_stocks[selected_code]
            print(stock_name)
            new_data = asyncio.run(connect(stock_name))  # 비동기 호출
            print(new_data)
            # `conclu` 처리
            columns = [
                'Stock Name', 'Time', 'Now', 'Contrast', 'Per', 'AskPrice',
                'BidPrice', 'Strength', 'Trading', 'Execution'
            ]
            new_df = pd.DataFrame(new_data, columns=columns)
            print(new_df)
            new_df['Time'] = new_df['Time'].astype(str).str.zfill(6)
            new_df['Time'] = new_df['Time'].apply(lambda x: datetime.strptime(x, '%H%M%S').time())
            new_df = new_df.sort_values(by='Time').reset_index(drop=True)

            # 새 데이터를 병합
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
            return selected_code, updated_df.to_json(orient='records')

        except Exception as e:
            print(f"Error fetching real-time data for {selected_code}: {e}")
            # 기존 데이터 유지
            return dash.no_update, existing_data if existing_data else []


    # 그래프 업데이트
    @graph.callback(
        Output("live-graph", "figure"),
        [Input("real-time-data", "data")],
        [State("selected-company", "data")],
        prevent_initial_call=True
    )
    def update_graph(real_time_data, selected_code):
        if not selected_code:
            return px.line(title="회사 코드를 선택하세요.")

        try:
            print("*"*50)
            print(type(real_time_data))
            print(real_time_data)
            if isinstance(real_time_data, str):
                real_time_data=json.loads(real_time_data)
            data = pd.DataFrame(real_time_data)
            print(data)
            fig = px.line(data, x="Time", y="Now", title=f"실시간 데이터 - {cj_stocks[selected_code]}")
            fig.update_layout(
                xaxis=dict(
                    tickangle=45  # X축 텍스트를 45도 기울임
                )
            )
            return fig
        except Exception as e:
            print(f"Error updating graph: {e}")
            return px.line(title=f"{cj_stocks[selected_code]} 체결 정보 로딩중...")

    return graph