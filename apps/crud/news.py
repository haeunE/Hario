# from flask import Flask, render_template, jsonify
# import requests
# from bs4 import BeautifulSoup
# from datetime import datetime, timedelta
# import threading
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
# from flask_wtf import CSRFProtect
# from flask_login import LoginManager
# from apps.config import config
# import os

# # 전역 변수로 보도자료를 저장
# latest_articles = []
# last_updated = None

# # config_key
# config_key = os.environ.get('FLASK_CONFIG_KEY')

# # SQLAlchemy 객체 생성
# db = SQLAlchemy()

# # CSRF 보안 객체 생성
# csrf = CSRFProtect()

# # Flask-Login의 LoginManager 객체 생성
# login_manager = LoginManager()

# def create_app():
#     #======================== 초기 앱 설정 ==============================
#     # Flask 앱 인스턴스 생성
#     app = Flask(__name__)

#     # 애플리케이션 설정 로드(local로)
#     app.config.from_object(config[config_key])

#     # 확장모듈 초기화
#     db.init_app(app)
#     Migrate(app, db)
#     csrf.init_app(app)  # CSRF 보호 활성화
#     login_manager.init_app(app)  # 사용자 인증 활성화

#     # 로그인되지 않은 사용자가 접근 시 리다이렉트할 페이지
#     login_manager.login_view = "auth.login"
#     login_manager.login_message = "로그인 후 사용 가능합니다."

#     #========================= 블루프린트 설정 ==============================
#     from apps.auth import views as auth_views
#     app.register_blueprint(auth_views.auth, url_prefix='/auth')

#     from apps.hire import views as hire_views
#     app.register_blueprint(hire_views.hire, url_prefix='/hire')

#     from apps.crud import views as crud_views
#     app.register_blueprint(crud_views.crud)
   
#     # #========================== department 초기 값 설정 ============================

#     # with app.app_context():
#     #   from apps.crud.models import Department, seed_userinfos  # 모델 임포트
#     #   Department.seed_departments()  # 초기 데이터 삽입
#     #   seed_userinfos()

#     # 에러 핸들러 설정
#     app.register_error_handler(404, page_not_found)
#     app.register_error_handler(500, internal_server_error)

#     # 최신 보도자료를 가져오는 기능
#     fetch_latest_articles()
#     schedule_fetch()

#     # 최신 뉴스 API 엔드포인트
#     @app.route('/latest-news', methods=['GET'])
#     def get_latest_news():
#         """
#         최신 보도자료를 반환하는 API 엔드포인트.
#         """
#         global latest_articles, last_updated
#         if not latest_articles or (datetime.now() - last_updated) > timedelta(days=1):
#             fetch_latest_articles()
#         return jsonify({
#             "last_updated": last_updated.strftime("%Y-%m-%d %H:%M:%S") if last_updated else "Never",
#             "articles": latest_articles
#         })

#     return app

# # 최신 뉴스 데이터를 가져오는 함수
# def fetch_latest_articles():
#     """
#     CJ News 웹사이트에서 최신 보도자료 2개를 스크랩.
#     """
#     global latest_articles, last_updated
#     try:
#         url = "https://cjnews.cj.net/category/news/%EB%B3%B4%EB%8F%84%EC%9E%90%EB%A3%8C/"
#         response = requests.get(url)
#         response.raise_for_status()

#         soup = BeautifulSoup(response.text, 'html.parser')
#         articles = soup.find_all('article', limit=2)  # 보도자료는 아티클 태그에 포함되어 있다고 가정

#         new_articles = []
#         for article in articles:
#             title = article.find('h2').get_text(strip=True)  # 제목 추출
#             link = article.find('a')['href']  # 링크 추출
#             summary = article.find('p').get_text(strip=True) if article.find('p') else ""  # 요약 추출

#             new_articles.append({
#                 "title": title,
#                 "link": link,
#                 "summary": summary
#             })

#         latest_articles = new_articles
#         last_updated = datetime.now()

#     except Exception as e:
#         print(f"Error fetching articles: {e}")

# # 매일 데이터를 갱신하는 스케줄러
# def schedule_fetch():
#     fetch_latest_articles()
#     threading.Timer(86400, schedule_fetch).start()  # 24시간(86400초)마다 실행

# # 에러 핸들러 함수
# def page_not_found(e):
#     return render_template('404.html'), 404

# def internal_server_error(e):
#     return render_template('500.html'), 500
