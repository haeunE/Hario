from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash, session
from flask_login import login_required, current_user
from apps.board.forms import BoardForm
from apps.crud.models import Board, Recommend, Comment, UserRole
from apps.app import db


board = Blueprint('board', __name__, template_folder='templates', static_folder='static')

@board.route("/<int:selection>", methods=["GET"])
@login_required
def index(selection):
    if not current_user.is_authenticated:
      return redirect(url_for('auth.login', next=request.url))  # 로그인 페이지로 이동 및 next에 현재 URL 저장
    
    department_id = request.args.get("department_id")

    if selection == 1 and current_user.userinfo.department_id == 99:
        return render_template("board/permission_denied.html")

    # 필터링 처리
    if department_id and int(department_id) != 0:
        query = Board.query.filter(Board.department_id == department_id, Board.selection == 1).order_by(Board.id.desc())
    else:
        if selection == 1:
            query = Board.query.filter(Board.selection == 1).order_by(Board.id.desc())
        elif selection == 2:
            query = Board.query.filter(Board.selection == 2).order_by(Board.id.desc())
        else:
            query = Board.query.filter(Board.selection == 3).order_by(Board.id.desc())


    # 최신 게시글 2개에 'is_new' 설정
    boards = query.all()  # 쿼리 객체로 유지하면서 all() 호출
    # 컬럼 총 개수
    board_total = query.count()

    for idx, board in enumerate(boards):
        board.is_new = idx < 2  # 상위 2개 게시글만 is_new=True

    # 페이징 처리
    page = request.args.get('page', type=int, default=1)
    boards = query.paginate(page=page, per_page=10)  # paginate() 호출

    block_size = 10
    current_block = (page - 1)//block_size + 1

    start_page = (current_block - 1)*block_size + 1
    end_page = min(current_block*block_size, boards.pages)

    has_prev_block = start_page > 1
    has_next_block = end_page < boards.pages

    page_start_number = board_total - (page - 1) * 10
    
    pagination = {
      "current_block" : current_block,
      "start_page" : start_page,
      "end_page" : end_page,
      "has_prev_block" : has_prev_block,
      "has_next_block" : has_next_block,
      "page_start_number": page_start_number,
    }

    return render_template("board/index.html", boards=boards.items, selection=selection, pagination=pagination, page=page)
  
@board.route("/new", methods=["GET", "POST"])
@login_required
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


    db.session.add(board)
    db.session.commit()
    return redirect(url_for("board.index", selection=board.selection))

  return render_template("board/new.html", form=form, user=current_user)

@board.route("/detail/<int:board_id>", methods=["GET", "POST"])
@login_required
def detail(board_id):
  if not current_user.is_authenticated:
      return redirect(url_for('auth.login', next=request.url))  # 로그인 페이지로 이동 및 next에 현재 URL 저장

  keyword = request.args.get('keyword')
  board = Board.query.get_or_404(board_id)

  if current_user.role == UserRole.SEEKER:
    if board.selection == 1 :
     return render_template("board/permission_denied.html")


  view_key = f"viewed_{board_id}"
  if request.method == "GET":
     # 세션에서 해당 게시글을 조회했는지 확인
        if not session.get(view_key):
            board.increment_views()  # 조회수 증가
            session[view_key] = True  # 세션에 조회 기록 저장

  # 페이징 처리
  page = request.args.get('page', type=int, default=1)
  comments = Comment.query.filter_by(board_id=board.id).order_by(Comment.id.desc()).paginate(page=page, per_page=10)  # paginate() 호출

  block_size = 10
  current_block = (page - 1)//block_size + 1

  start_page = (current_block - 1)*block_size + 1
  end_page = min(current_block*block_size, comments.pages)

  has_prev_block = start_page > 1
  has_next_block = end_page < comments.pages
  
  pagination = {
    "current_block" : current_block,
    "start_page" : start_page,
    "end_page" : end_page,
    "has_prev_block" : has_prev_block,
    "has_next_block" : has_next_block
  }         

  return render_template("board/detail.html", board=board, comments=comments, pagination=pagination, page=page, keyword=keyword)


@board.route("/update/<int:board_id>", methods=["GET", "POST"])
@login_required
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



@board.route("/delete/<int:board_id>", methods=["DELETE"])
@login_required
def delete(board_id):
    Board.query.filter_by(id=board_id).delete()
    db.session.commit()


    return jsonify({"message": "게시물이 삭제되었습니다."}), 200


# 추천
@board.route("/recommend/<int:board_id>", methods=["POST"])
def recommend(board_id):
   recommend_entry = Recommend.query.filter_by(user_id=current_user.id, board_id=board_id).first()
   if recommend_entry:
      db.session.delete(recommend_entry)
      db.session.commit()
   else:
      new_recommend = Recommend(user_id=current_user.id, board_id=board_id)
      db.session.add(new_recommend)
      db.session.commit()
   return redirect(url_for("board.detail", board_id=board_id))

# 댓글
@board.route("/comment/new/<int:board_id>", methods=["POST"])
@login_required
def comment_new(board_id):
   board = Board.query.get_or_404(board_id)

   content = request.form.get("content") 

   if not content or content.strip() == "":
      flash("댓글 내용을 넣어 등록해 주세요", "error")
      return redirect(url_for("board.detail", board_id=board_id))

   comment = Comment(
      content = content,
      user = current_user,
      board = board
   )
   db.session.add(comment)
   db.session.commit()

   return redirect(url_for("board.detail", board_id=board_id))
  
@board.route("/comment/update/<int:comment_id>", methods=["PUT"])
def comment_update(comment_id):
   data = request.get_json()
   comment = Comment.query.get_or_404(comment_id)
   comment.content = data.get('content')

   db.session.add(comment)
   db.session.commit()

   return jsonify({"message": "댓글이 수정되었습니다."}), 200

@board.route("/comment/delete/<int:comment_id>", methods=["DELETE"])
def comment_delete(comment_id):
   Comment.query.filter_by(id=comment_id).delete()
   db.session.commit()
   return jsonify({"message":"댓글이 삭제 되었습니다."}), 200


# 더미 데이터 생성
@board.route('/dummy')
def make_dummy():
    create_boards_and_comments()  # Dummy 데이터 생성 함수 호출
    return "더미 데이터가 생성되었습니다."

# 더미 게시글 및 댓글 생성 함수
def create_boards_and_comments():
    users = [(4, 50), (3, 50)]
    
    for user_id, start_index in users:
        for i in range(50):
            board = Board(
                subject=f'임시제목{start_index + i}',
                content=f'임시내용{start_index + i}',
                user_id=user_id,
                selection=1,
                department_id=user_id
            )
            db.session.add(board)

    db.session.commit()  # 한 번에 커밋

    # 댓글 생성
    for i in range(50):
        comment = Comment(
            content=f'임시내용{i+50}',
            user_id=3,
            board_id=200
        )
        db.session.add(comment)

    db.session.commit()  # 한 번에 커밋