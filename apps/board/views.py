from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from apps.board.forms import BoardForm
from apps.crud.models import User, Board, Recommend
from apps.app import db

from datetime import datetime, timedelta

board = Blueprint('board', __name__, template_folder='templates', static_folder='static')

@board.route("/<int:selection>", methods=["GET"])
def index(selection):
    department_id = request.args.get("department_id")

    if department_id:
        boards = Board.query.filter_by(department_id=department_id, selection=1).order_by(Board.created_at.desc()).all()
    else:
        if selection == 1:
            boards = Board.query.filter_by(selection=1).order_by(Board.created_at.desc()).all()
        elif selection == 2:
            boards = Board.query.filter_by(selection=2).order_by(Board.created_at.desc()).all()
        else:
            boards = Board.query.filter_by(selection=3).order_by(Board.created_at.desc()).all()

    # 최신 게시글 2개에 'is_new' 설정
    # enumerate : 반복 가능한 객체(예: 리스트, 튜플 등)를 순회하면서 인덱스와 값을 동시에 반환하는 함수
    for idx, board in enumerate(boards):
        board.is_new = idx < 2  # 상위 2개 게시글만 is_new=True

    return render_template("board/index.html", boards=boards, selection=selection)
  
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

# 추천
@board.route("/recommend/<int:board_id>", methods=["POST"])
def recommend(board_id):
   board = Board.query.filter_by(id=board_id).first()
   recommand_entry = Recommend.query.filter_by(user_id=current_user.id, board_id=board_id).first()
   if recommand_entry:
      db.session.delete(recommand_entry)
      db.session.commit()
   else:
      new_recommend = Recommend(user_id=current_user.id, board_id=board_id)
      db.session.add(new_recommend)
      db.session.commit()
   return redirect(url_for("board.detail", board_id=board_id))