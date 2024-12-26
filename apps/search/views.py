from flask import Blueprint, request, render_template
from apps.crud.models import Board, Department

search = Blueprint("search", __name__, template_folder="templates", static_folder="static")

@search.route("/search", methods=["GET"])
def search_keyword():
  keyword = request.args.get("keyword")

  boards = (Board.query.join(Department)
      .filter(
          (Board.content.ilike(f"%{keyword}%")) | 
          (Board.subject.ilike(f"%{keyword}%")) | 
          (Department.name.ilike(f"%{keyword}%"))
      )
      .order_by(Board.id.desc())
  )
  board_total = boards.count()
 
  # 페이징 처리
  page = request.args.get('page', type=int, default=1)
  boards = boards.paginate(page=page, per_page=10)  # paginate() 호출

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

  return render_template("search/search.html", boards=boards, pagination=pagination, keyword=keyword)