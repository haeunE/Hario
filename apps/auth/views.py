from flask import Blueprint, render_template, redirect, url_for

auth = Blueprint("auth", __name__, template_folder="templates/auth", static_folder="static")

@auth.route("/")
def index():
  return render_template("index.html")