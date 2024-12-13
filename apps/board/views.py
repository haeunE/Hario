from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
board = Blueprint('board', __name__, template_folder='templates', static_folder='static')


@board.route("/")
def index():
  return render_template("board/index.html")