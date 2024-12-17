from flask import Blueprint, render_template


graph = Blueprint('graph', __name__, template_folder="templates", static_folder="static")
@graph.route('/company')
def company():
    return render_template('graph/company.html')

@graph.route('/covid')
def covid():
    return render_template('graph/covid.html')