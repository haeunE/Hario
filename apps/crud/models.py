from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from enum import Enum
import random
from sqlalchemy.orm import validates
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

    userinfo_id = db.Column(db.Integer, db.ForeignKey("userinfo.id", ondelete='CASCADE'), nullable=False)
    userinfo = db.relationship('Userinfo', backref=db.backref('user', uselist=False))

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

# Userinfo 모델
class Userinfo(db.Model):
    __tablename__ = 'userinfo'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    birthdate = db.Column(db.DateTime, nullable=False, default=datetime.now)
    tel = db.Column(db.String(255), nullable=False)

    department_id = db.Column(db.Integer, db.ForeignKey("department.id", ondelete='CASCADE'), nullable=False)
    uniquenum = db.Column(db.Integer, unique=True, nullable=False)

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

    def __repr__(self):
        return f"<Department(id={self.id}, name={self.name})>"

    @staticmethod
    def seed_departments():
        """초기 데이터 삽입"""
        if not Department.query.first():  # 데이터가 없는 경우에만 삽입
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
            db.session.commit()
            print("Departments seeded!")
