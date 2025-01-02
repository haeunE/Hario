from flask import  Blueprint, render_template # from은 도구가 들어있는 상자 import는 도구에들어있는 여러 도구들을 가져옴

 
react = Blueprint('react', __name__, template_folder='templates/react', static_folder='static')
# Blueprint는 클래스로 'react'는 블루프린트 이름 __name__은 현재의 모듈 이름 그리고 차례로 이 블루프린트에서 사용할
# 템플릿과 정적파일을 지정한 것

@react.route("/") # URL 경로를 특정 함수에 연결하는 작업을 함
def index(): # 함수    
    return render_template("react.html") # index.html를 보여주게 함

@react.route("/<data>")
def CJ1(data):
    return render_template(f"{data}.html")
