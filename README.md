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

# DB 설정

```
flask db init
flask db migrate
flask db upgrade
```
