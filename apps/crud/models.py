from flask_login import UserMixin
from datetime import datetime
from enum import Enum
import random
from apps.app import db, login_manager
from flask_login import UserMixin

# 비밀번호 해싱, 비밀번호 해싱 확인
from werkzeug.security import generate_password_hash, check_password_hash


# User Role Enum
class UserRole(Enum):
    ADMIN = "admin"
    WORKER = "worker"
    SEEKER = "seeker"

# User 모델
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.SEEKER)

    # Userinfo와 1대1 관계 설정
    userinfo_id = db.Column(db.Integer, db.ForeignKey("userinfo.id", ondelete='CASCADE'), nullable=False)
    userinfo = db.relationship('Userinfo', back_populates='user', uselist=False, lazy='joined')
  
    @property
    def password(self):
        raise AttributeError("비밀번호는 접근이 불가능 합니다.")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_duplicate_username(self):
        return User.query.filter_by(username=self.username).first() is not None

# 로그인 성공 + 특정 요청 -> 세션에 저장 된 id이용해, DB에 정보 가져옴
@login_manager.user_loader
def load_user(user_id):
  return User.query.get(user_id)  

# Userinfo 모델
class Userinfo(db.Model):
    __tablename__ = 'userinfo'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    birthdate = db.Column(db.DateTime, nullable=False)
    tel = db.Column(db.String(255), nullable=False, unique = True)
    email = db.Column(db.String(255), nullable=False, unique =True)

    department_id = db.Column(db.Integer, db.ForeignKey("department.id", ondelete='CASCADE'), nullable=False)
    uniquenum = db.Column(db.Integer, unique=True, nullable=False)

    # User와 1대1 관계
    user = db.relationship('User', back_populates='userinfo', uselist=False)

    def is_duplicate_tel(self):
        return Userinfo.query.filter_by(tel = self.tel).first() is not None
    
    def is_duplicate_email(self):
        return Userinfo.query.filter_by(email = self.email).first() is not None

    @staticmethod
    def generate_random_number():
        """6자리 랜덤 숫자 생성"""
        return random.randint(100000, 999999)

    @classmethod
    def generate_unique_number(cls):
        """중복되지 않은 6자리 랜덤 숫자 생성"""
        while True:
            num = cls.generate_random_number()
            if not db.session.query(cls).filter_by(uniquenum=num).first():
                return num

    def __init__(self, uniquenum=None, **kwargs):
        """고유 번호를 자동 생성하거나 외부에서 제공받은 값 사용"""
        super().__init__(**kwargs)
        self.uniquenum = uniquenum or self.generate_unique_number()

# Department 모델
class Department(db.Model):
    __tablename__ = 'department'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
   
class Board(db.Model):
    __tablename__ = "board"
    id = db.Column(db.Integer, primary_key = True)
    subject = db.Column(db.String(255),nullable = False)
    content = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    # 직장인(1) / 취준생(2) / 모두(3) 페이지 어디에 저장
    selection = db.Column(db.Integer, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = db.relationship("User", backref=db.backref("boards"))

    # 부서 
    department_id = db.Column(db.Integer, db.ForeignKey("department.id", ondelete="CASCADE"), nullable=False)
    department = db.relationship("Department", backref=db.backref("boards"))

    # 조회수
    views = db.Column(db.Integer, default=0, nullable=False)

    # 추천 기능 관계 설정 - 다대다
    recommender = db.relationship("User", secondary="recommend", backref=db.backref("recommender_list"))

    # 게시글에 조회수를 증가시키는 메소드
    def increment_views(self):
        self.views += 1
        db.session.commit()

    # 페이지 이전, 이후
    def get_pre_board(self):
        return(
            Board.query.filter(Board.selection == self.selection, Board.id < self.id)
            .order_by(Board.id.desc())
            .first()
        ) 
    def get_next_board(self):
        return(
            Board.query.filter(Board.selection == self.selection, Board.id > self.id)
            .order_by(Board.id.asc())
            .first()
        )

class Recommend(db.Model):
    __tablename__ = "recommend"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = db.relationship("User", backref=db.backref("recommends"))
    board_id = db.Column(db.Integer, db.ForeignKey("board.id", ondelete="CASCADE"), nullable=False)


class Comment(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = db.relationship("User", backref=db.backref("comments"))
    board_id = db.Column(db.Integer, db.ForeignKey("board.id", ondelete="CASCADE"), nullable=False)
    board = db.relationship("Board", backref=db.backref("comments"))


def seed_initial_data():
    """초기 데이터를 삽입하는 통합 함수"""
    # 부서 데이터 삽입
    if not Department.query.first():
        departments = [
            {"id": 99, "name": "소속없음"},
            {"id": 1, "name": "대한통운"},
            {"id": 2, "name": "제일제당"},
            {"id": 3, "name": "프레시웨이"},
            {"id": 4, "name": "ENM"},
            {"id": 5, "name": "CGV"},
            {"id": 6, "name": "스튜디오드래곤"},
            {"id": 7, "name": "CJ 씨푸드"},
            {"id": 8, "name": "CJ 바이오사이언스"},
        ]
        for dept in departments:
            db.session.add(Department(**dept))
        print("Department 데이터가 삽입되었습니다.")

    # Userinfo 데이터 삽입
    if not Userinfo.query.first():
        userinfos = [
            {"name": "홍길동", "birthdate": "1980-01-01", "tel": "01012345678", "email": "honggildong@example.com", "department_id": 1},
            {"name": "김철수", "birthdate": "1990-05-15", "tel": "01023456789", "email": "kimchulsoo@example.com", "department_id": 2},
            {"name": "이영희", "birthdate": "1985-08-25", "tel": "01034567890", "email": "leeyounghee@example.com", "department_id": 3},
            {"name": "박민수", "birthdate": "1995-02-10", "tel": "01045678901", "email": "parkminsoo@example.com", "department_id": 4},
            {"name": "최지은", "birthdate": "1992-06-30", "tel": "01056789012", "email": "choijieun@example.com", "department_id": 5},
        ]
        for user_data in userinfos:
            userinfo = Userinfo(**user_data)
            db.session.add(userinfo)
        print("Userinfo 데이터가 삽입되었습니다.")

    # User 데이터 삽입
    if not User.query.first():
        users = [
            {"username": "admin", "password": "admin123", "role": UserRole.ADMIN, "userinfo_id": 1},
            {"username": "worker1", "password": "worker123", "role": UserRole.WORKER, "userinfo_id": 2},
            {"username": "worker", "password": "123", "role": UserRole.WORKER, "userinfo_id": 3},
            {"username": "아이디", "password": "123", "role": UserRole.WORKER, "userinfo_id": 4},
        ]
        for user_data in users:
            user = User(username=user_data["username"], role=user_data["role"], userinfo_id=user_data["userinfo_id"])
            user.password = user_data["password"]  # setter를 통해 비밀번호 해싱
            db.session.add(user)
        print("User 데이터가 삽입되었습니다.")

    # 모든 데이터 커밋
    db.session.commit()
    print("초기 데이터가 성공적으로 삽입되었습니다.")


