import plotly.io as pio
import plotly.express as px
from .pre_covid import day_covid
import os

def save_sessionfig() : 
  if not os.path.exists("apps/graph/static/session_fig.json"):
      # 그래프 생성
      session_fig = px.bar(day_covid, title="한국 코로나 집계", color=day_covid.index, animation_frame="날짜", text_auto='.2s')
      
      # 그래프를 JSON 파일로 저장
      pio.write_json(session_fig, "apps/graph/static/session_fig.json")
      print("Graph saved as JSON.")
  else:
      print("Graph JSON already exists.")