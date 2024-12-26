from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import Length, DataRequired

# 부서 선택? 직장인, 취준생
class BoardForm(FlaskForm):
  subject = StringField(
    "제목",
    validators=[
      DataRequired(message="제목은 필수 입력해주세요."),
      Length(min=3, max=50, message="3자 이상 50자 이내로 작성해주세요.")
    ]
  )

  content = TextAreaField(
    "내용",
    validators=[
      DataRequired(message="내용은 필수 입력해주세요.")
    ],
    render_kw={'rows':10}
  )

  submit = SubmitField('등록')