import plotly.io as pio
import plotly.express as px
from .pre_covid import day_covid
import os

def save_sessionfig() : 
  if not os.path.exists("apps/graph/static/session_fig.json"):
      # 그래프 생성
      session_fig = px.bar(day_covid, color=day_covid.index, animation_frame="날짜", text_auto='.2s')
      session_fig.update_layout(
        height = 700,
        xaxis_title='분류',
        yaxis_title='인원 수',
        showlegend=True,
        font=dict(family="Arial, sans-serif", size=12),
        title_font=dict(size=24),
        plot_bgcolor="#f5f5f5",
        xaxis=dict(autorange=True),  # X축 자동 범위
        yaxis=dict(autorange=True),  # Y축 자동 범위
        sliders=[{
            "x": 0.05,  # 슬라이더를 화면의 왼쪽에 배치 (0 ~ 1 사이의 값, 0.05로 시작)
            "xanchor": "left",  # 슬라이더의 왼쪽을 기준으로 배치
            "y": 0,  # y 값은 아래쪽에 위치 (y 값은 조정 가능)
            "yanchor": "top"  # 슬라이더의 상단을 기준으로 위치
        }],
        updatemenus=[{
            "buttons": [
                {
                    "args": [None, {"frame": {"redraw": True}, "fromcurrent": True}],
                    "label": "Play",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                    "label": "Stop",
                    "method": "animate"
                }
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 10},
            "showactive": False,
            "type": "buttons",
            "x": 1,  # 버튼을 화면 오른쪽에 배치
            "xanchor": "left",  # 버튼이 왼쪽에서 시작하도록 설정
            "y": -0.19,  # 버튼을 슬라이더와 동일한 y 위치로 배치
            "yanchor": "top"  # 버튼의 상단을 기준으로 위치
        }]
    )
      # 그래프를 JSON 파일로 저장
      pio.write_json(session_fig, "apps/graph/static/session_fig.json")
      print("Graph saved as JSON.")
  else:
      print("Graph JSON already exists.")