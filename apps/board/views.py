from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from apps.board.forms import BoardForm
from apps.crud.models import User, Board, Recommend
from apps.app import db

board = Blueprint('board', __name__, template_folder='templates', static_folder='static')

@board.route("/<int:selection>")
def index(selection):
  is_show = False

  if selection == 1:
    boards = Board.query.filter_by(selection=1).order_by(Board.created_at.desc()).all()  # 최신 게시글이 위로 오도록 정렬
    # 부서별로 선택하면 보이게
    is_show = True 

  elif selection == 2:
    boards = Board.query.filter_by(selection=2).order_by(Board.created_at.desc()).all()  # 최신 게시글이 위로 오도록 정렬
  else:
    boards = Board.query.filter_by(selection=3).order_by(Board.created_at.desc()).all()  # 최신 게시글이 위로 오도록 정렬

  return render_template("board/index.html", boards=boards, is_show=is_show)

  
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
    return redirect(url_for("board.index", selection=board.selection))

  return render_template("board/new.html", form=form, user=current_user)

@board.route("/detail/<int:board_id>", methods=["GET", "POST"])
def detail(board_id):
  board = Board.query.get_or_404(board_id)

  return render_template("board/detail.html", board=board)


@board.route("/update/<int:board_id>", methods=["GET", "POST"])
def update(board_id):
  board = Board.query.get_or_404(board_id)
  form = BoardForm()

  if form.validate_on_submit():
    board.subject = form.subject.data
    board.content = form.content.data
    
    db.session.add(board)
    db.session.commit()
    return redirect(url_for("board.detail", board_id=board_id))

  return render_template("board/update.html", board=board, form=form, user=current_user)



@board.route("/delete/<int:board_id>/<int:board_sel>", methods=["POST"])
def delete(board_id, board_sel):
  Board.query.filter_by(id=board_id).delete()
  db.session.commit()
  return redirect(url_for("board.index", selection=board_sel))