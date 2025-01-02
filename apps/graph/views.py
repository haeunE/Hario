from flask import Blueprint, render_template,redirect,url_for,request,jsonify
from apps.graph.preprocess.now_stock import now_stock
from apps.app import csrf  
from threading import Thread
from apps.graph.preprocess.live_stock import connect


graph = Blueprint('graph', __name__, template_folder="templates", static_folder="static")
# 현재 선택된 종목 (기본값)


@graph.route('/company')
def company():
    return render_template('graph/company.html')

@graph.route('/covid')
def covid():
    return render_template('graph/covid.html')

@graph.route('/stock')
def stock():
    return render_template("graph/stock.html")

@graph.route("/stocklive")
def stocklive():
    return render_template("graph/stock_live.html")

# @graph.route("/current")
# def current():
#     return render_template("graph/current.html")

# @graph.route("/current/<code>", methods=["post"])
# @csrf.exempt
# def current_stock(code):
#     try:
#         # code에 따른 처리를 위한 함수 호출
#         now_stock(code)  # 주식 데이터 처리 함수
        
#     except Exception as e:
#         # 에러 처리 (예: 400 Bad Request)
#         return f"Error occurred: {str(e)}", 400