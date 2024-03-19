import math

from flask import Blueprint, render_template, request
from flask_jwt_extended import jwt_required
from database import db

bp = Blueprint('routes', __name__)

PAGE_SIZE = 7

@bp.route('/')
def home():
    return render_template('index.html')

@bp.route('/login')
def login():
    return render_template('login.html')
    
@bp.route('/sign_in')
def sign_in():
    return render_template('sign_in.html')

@bp.route('/list')
@jwt_required()
def list():
    page = request.args.get('page', 1, type=int)
    users = db.jungle.find({}, {"_id": 0}).skip((page-1) * PAGE_SIZE).limit(PAGE_SIZE)
    total_count = db.jungle.find({}).count()
    last_page_num = math.ceil(total_count / PAGE_SIZE)
    user_list = [user for user in users]

    return render_template('list.html', data=user_list)

# @bp.route('/get_user')
# def get_user():
#     return render_template('get_user.html')

@bp.route('/quiz')
def quiz():
    return render_template('quiz.html')

@bp.route('/result')
def result():
    return render_template('result.html')