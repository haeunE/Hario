import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
from apps.graph.preprocess.pre_covid import day_covid




#==========================================================================================
# Dash 애플리케이션
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Plotly 그래프
fig = px.bar(day_covid, title="한국 코로나 집계", color=day_covid.index, animation_frame="날짜", text_auto='.2s')
# 애니메이션 속도 조정
fig.update_layout(
    xaxis_title='분류',
    yaxis_title='인원 수',
    showlegend=True,
    font=dict(family="Arial, sans-serif", size=12),
    title_font=dict(size=24),
    plot_bgcolor="#f5f5f5"
)

# 레이아웃 구성
app.layout = html.Div([
    dbc.Container([
        html.H1("한국 코로나 집계", style={'textAlign': 'center', 'color': '#007bff', 'fontSize': '32px'}),
        html.Div(
            dcc.Graph(
                id='covid-bar-chart',
                figure=fig
            ), style={'padding': '30px'}
        ),
    ], fluid=True)
])

if __name__ == '__main__':
    app.run_server(debug=True)
