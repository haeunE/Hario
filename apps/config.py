import  secrets
import os
from pathlib import Path

dir= os.path.dirname(__file__)
image_dir = Path(__file__).parent.parent

class BaseConfig:
  SECRET_KEY = secrets.token_urlsafe(32)
  WTF_CSRF_SECRET_KEY = secrets.token_urlsafe(32)
  UPLOAD_FOLDER = str(Path(image_dir,"apps","images"))

#로컬환경
class LocalConfig(BaseConfig):
  SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://root:1234@localhost:3306/hariodb'
  SQLALCHEMY_TRACK_MODIFICATIONS=False #객체 변경사항 감지
  SQLAlCHEMY_ECHO=True #console.log 확인 가능

#테스트 환경
class TestingConfig(BaseConfig):
  SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://root:1234@localhost:3306/hariodb'
  SQLALCHEMY_TRACK_MODIFICATIONS=False #객체 변경사항 감지
  SQLAlCHEMY_ECHO=True #console.log 확인 가능

#배포
class ProductionConfig(BaseConfig):
  SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://root:1234@localhost:3306/hariodb'
  SQLALCHEMY_TRACK_MODIFICATIONS=False #객체 변경사항 감지
  SQLAlCHEMY_ECHO=True #console.log 확인 가능

config ={
  "local" : LocalConfig,
  "testing" : TestingConfig,
  "production" : ProductionConfig
}
