from apps.app import db, login_manager
from flask_login import UserMixin

from datetime import datetime
# from werkzeug.security import

class User(db.Model.UserMixin):
  __tablename__ = "users"
