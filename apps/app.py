from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from flask_login import LoginManager
from apps.config import config
import os
from flask_login import LoginManager
from .graph import graph
from .graph.graph import company_dash,korea_covid,stock_dash


# config_key
config_key = os.environ.get('FLASK_CONFIG_KEY')

# SQLAlchemy 객체 생성
db = SQLAlchemy()

# CSRF 보안 객체 생성
csrf = CSRFProtect()

# Flask-Login의 LoginManager 객체 생성
login_manager = LoginManager()

def create_app():
  #======================== 초기 앱 설정 ==============================
   # Flask 앱 인스턴스 생성
  app = Flask(__name__)
  dash_app = company_dash(app)
  covid_app = korea_covid(app)
  stock_app = stock_dash(app)


  for view_func in dash_app.server.view_functions:
        if view_func.startswith('/graph/company/'):
            csrf.exempt(dash_app.server.view_functions[view_func])
  for view_func in covid_app.server.view_functions:
        if view_func.startswith('/graph/covid/'):
            csrf.exempt(covid_app.server.view_functions[view_func])
  for view_func in stock_app.server.view_functions:
        if view_func.startswith('/graph/stock/'):
            csrf.exempt(stock_app.server.view_functions[view_func])

  # 애플리케이션 설정 로드(local로)
  app.config.from_object(config[config_key])

  # 확장모듈 초기화
  db.init_app(app)
  Migrate(app, db)
  csrf.init_app(app)  # CSRF 보호 활성화
  login_manager.init_app(app)  # 사용자 인증 활성화

  # 로그인되지 않은 사용자가 접근 시 리다이렉트할 페이지
  login_manager.login_view = "auth.login"
  login_manager.login_message = "로그인 후 사용 가능합니다."

  #========================= 블루프린트 설정 ==============================

  from apps.auth import views as auth_views
  app.register_blueprint(auth_views.auth, url_prefix='/auth')


  from apps.crud import views as crud_views
  app.register_blueprint(crud_views.crud)

  from apps.graph import views as graph_views
  app.register_blueprint(graph_views.graph, url_prefix='/graph')
  


  from apps.board import views as board_views
  app.register_blueprint(board_views.board, url_prefix='/board')
      
    # #========================== department 초기 값 설정 ============================

  # with app.app_context():
  #   from apps.crud.models import seed_initial_data  # 모델 임포트
  #   seed_initial_data()

  # 에러 핸들러 설정
  app.register_error_handler(404, page_not_found)
  app.register_error_handler(500, internal_server_error)

  return app


# 에러 핸들러 함수
def page_not_found(e):
    return render_template('404.html'), 404

def internal_server_error(e):
    return render_template('500.html'), 500
