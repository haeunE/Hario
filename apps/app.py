from flask import Flask, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from apps.config import config
import os
from flask_login import LoginManager

#config_key
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

  # 애플리케이션 설정 로드(local로)
  app.config.from_object(config[config_key])
  
  # 확장모듈 초기화
  db.init_app(app)
  Migrate(app, db)
  csrf.init_app(app) # CSRF 보호 활성화
  login_manager.init_app(app) # 사용자 인증 활성화

  # 로그인되지 않은 사용자가 접근 시 리다이렉트할 페이지
  login_manager.login_view = "auth.login"
  login_manager.login_message = "로그인 후 사용 가능합니다."

  #========================= 블루프린트 설정 ==============================

  from apps.auth import views as auth_views
  app.register_blueprint(auth_views.auth, url_prefix='/auth')

  from apps.hire import views as hire_views
  app.register_blueprint(hire_views.hire, url_prefix='/hire')

  from apps.crud import views as crud_views
  app.register_blueprint(crud_views.crud)

  #========================== 에러 핸들러 설정 ============================
  app.register_error_handler(404, page_not_found)
  app.register_error_handler(500, internal_server_error)

  
  # #========================== department 초기 값 설정 ============================

  # with app.app_context():
  #   from apps.crud.models import Department, seed_userinfos  # 모델 임포트
  #   Department.seed_departments()  # 초기 데이터 삽입
  #   seed_userinfos()


  return app

# 에러 핸들러 함수
def page_not_found(e):
  return render_template('404.html'),404

def internal_server_error(e):
  return render_template('500.html'),500
