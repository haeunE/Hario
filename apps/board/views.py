from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from apps.board.forms import BoardForm
from apps.crud.models import User, Board, Recommend
from apps.app import db

board = Blueprint('board', __name__, template_folder='templates', static_folder='static')

@board.route("/")
def index():

  # 직장인, 취준생 같은 html 사용해서 따로 정보 전달

  # 부서 별로 선택하는 기능 넣어야 함

  return render_template("board/index.html")


@board.route("/new", methods=["GET", "POST"])
def new():
  form = BoardForm()

  if form.validate_on_submit():
    board = Board(
      selection = request.form.get("board_type"),
      subject = form.subject.data,
      content = form.content.data,
      user = current_user,
      department_id = current_user.userinfo.department_id
    )

    print(board.selection)
    print(board.department_id)

    db.session.add(board)
    db.session.commit()
    return redirect(url_for("board.index"))


  return render_template("board/new.html", form = form, user = current_user)