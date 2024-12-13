from flask import Blueprint, render_template, jsonify
import requests

crud = Blueprint('crud', __name__, template_folder="templates", static_folder="static")

@crud.route("/")
def index():
    return render_template("index.html")
