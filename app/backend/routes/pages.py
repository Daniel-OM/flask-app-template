
from flask import Blueprint, render_template
from flask_login import login_required


pages_api = Blueprint(name='pages_api', import_name=__name__)

@pages_api.route(rule='/', methods=['GET'])
@pages_api.route(rule='/home', methods=['GET'])
def home() -> str:
    return render_template(template_name_or_list='../../frontend/templates/home.html')

@pages_api.route(rule='/login', methods=['GET'])
def login() -> str:
    return render_template(template_name_or_list='../../frontend/templates/login.html')

@pages_api.route(rule='/dashboard', methods=['GET'])
@login_required
def dashboard() -> str:
    return render_template(template_name_or_list='../../frontend/templates/loged.html')