from flask import Blueprint, render_template

bp = Blueprint('routes', __name__)

@bp.route('/main')
def home():
    return render_template('index.html')

# @bp.route('/login')
# def login():
#     return render_template('login.html')
    
# @bp.route('/sign_in')
# def main():
#     return render_template('sign_in.html')

# @bp.route('/list')
# def main():
#     return render_template('list.html')

# @bp.route('/get_user')
# def main():
#     return render_template('get_user.html')

@bp.route('/quiz')
def main():
    return render_template('quiz.html')