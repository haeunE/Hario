from flask import Blueprint, render_template, jsonify
import requests

from apps.crud.news import crawl_naver_news 

crud = Blueprint('crud', __name__, template_folder="templates", static_folder="static")

@crud.route("/")
def index():
    news_items = crawl_naver_news()
    return render_template("index.html", news_items = news_items)
