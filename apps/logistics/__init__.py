from flask import Flask
from .views import logistics

app = Flask(__name__)

# 블루프린트 등록
app.register_blueprint(logistics, url_prefix='/logistics')