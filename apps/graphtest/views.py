from flask import Blueprint, render_template

graphtest = Blueprint('graphtest', __name__, template_folder="templates", static_folder="static")
@graphtest.route('/')
def home():
    return render_template('index.html')