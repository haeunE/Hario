from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, DateField
from wtforms.validators import Length, DataRequired, Regexp, Email

class UserForm(FlaskForm):
  username = StringField(
    "아이디",
    validators=[
      DataRequired(message="아이디 필수 입력 해주세요."),
      Length(max=30, message="30자 이내로 입력해 주세요")
    ]
  )

  password = PasswordField(
    "비밀번호",
    validators=[
      DataRequired(message="비밀번호 필수 입력 해주세요.")
    ]
  )

  submit = SubmitField("회원가입")



class UserinfoForm(FlaskForm):
  name = StringField(
    "이름",
    validators=[
      DataRequired(message="이름 필수 입력해 주세요."),
      Length(min=2, max=6, message="정확한 이름을 입력해 주세요.")
    ]
  )

  birthdate = DateField(
    "생년월일",
    format='%Y-%m-%d',
    validators=[
      DataRequired(message="생년월일 필수 입력해 주세요.")
    ]
  )

  tel = StringField(
    "전화번호",
    validators=[
        DataRequired(message="전화번호 필수 입력해 주세요."),
        Regexp(
            regex=r"^010\d{8}$",
            message="전화번호는 '010-xxxx-xxxx' 또는 '010xxxxxxxx' 형식이어야 합니다."
        )
    ]
  )

  email = EmailField(
    "이메일",
    validators=[
       DataRequired(message="이메일 필수 입력해 주세요."),
       Email(message="유효한 이메일 주소를 입력해 주세요.")
    ]
  )

  submit = SubmitField("회원정보 입력")
