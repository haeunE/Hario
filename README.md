# Flask(Full Stack) Project 
Flask, html, css, javaScript, MySQL 이용한 CJ 기업의 Covid19 영향 분석

## :computer: 프로젝트 소개
이 웹사이트는 CJ그룹의 코로나19 팬데믹 기간 동안 사업 부문별로 겪은 타격과 수요 증가를 분석하는 플랫폼입니다. 블라인드와 유사한 익명 게시판 형식을 적용해, CJ그룹 직원뿐 아니라 업계 관계자들이 자유롭게 경험과 데이터를 공유할 수 있도록 설계했습니다.

## :watch: 개발기간
24.12.06 ~ 24.12.27

## :cd: 멤버구성
- 팀장(이하은) :
- 팀원(심하나) :
- 팀원(조하경) :
- 팀원(이창용) : 

## :family: 개발환경
- Flask==3.1.0
- SQLAlchemy==2.0.36

## :pushpin: 주요기능


# Clone 후 해야할 것

---

## 가상환경 생성

```
py -3.11 -m venv venv
```

## 가상환경 활성화

```
.\venv\Scripts\activate
```

## 라이브러리 설치

```
pip install -r .\requirements.txt
```

## .env파일 생성하고 코드 넣어주기

```
FLASK_APP=apps.app.py
FLASK_DEBUG=True
FLASK_CONFIG_KEY=local
```

## requirements.txt 설정
```
pip install -r requirements.txt
```

## DB 설정

```
flask db init
flask db migrate
flask db upgrade
```
