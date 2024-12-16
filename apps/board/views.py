from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from apps.board.forms import BoardForm
from apps.crud.models import User, Board, Recommend
from apps.app import db

board = Blueprint('board', __name__, template_folder='templates', static_folder='static')

@board.route("/")
def index():
  section = request.args.get('section', type=int)
  
  if section == 1:
    boards = Board.query.filter_by(selection=1).order_by(Board.created_at.desc()).all()  # 최신 게시글이 위로 오도록 정렬
  elif section == 2:
    boards = Board.query.filter_by(selection=2).order_by(Board.created_at.desc()).all()  # 최신 게시글이 위로 오도록 정렬
  else:
    boards = Board.query.filter_by(selection=3).order_by(Board.created_at.desc()).all()  # 최신 게시글이 위로 오도록 정렬

  return render_template("board/index.html", boards=boards)

  


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

  return render_template("board/new.html", form=form, user=current_user)
