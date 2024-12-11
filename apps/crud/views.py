from flask import Blueprint, render_template

crud = Blueprint('crud', __name__, template_folder="templates")

@crud.route("/")
def index():
 return render_template("crud/index.html")