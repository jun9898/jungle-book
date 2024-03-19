from flask import Blueprint, render_template

bp = Blueprint('routes', __name__)

@bp.route('/')
def main():
    return render_template('index.html')

# @bp.route('/login')
# def login():
#     return render_template('login.html')
    
# @bp.route('/sign_in')
# def sign_in():
#     return render_template('sign_in.html')

# @bp.route('/list')
# def list():
#     return render_template('list.html')

# @bp.route('/get_user')
# def get_user():
#     return render_template('get_user.html')

@bp.route('/quiz')
def quiz():
    return render_template('quiz.html')

@bp.route('/result')
def result():
    return render_template('result.html')