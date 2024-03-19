import math
import jwt
from flask import Blueprint, render_template, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from secret_key import SECRET_KEY
from decorator import require_access_token

bp = Blueprint('routes', __name__)

PAGE_SIZE = 6

@bp.route('/')
def home():
    return render_template('index.html')

@bp.route('/login')
def login():
    return render_template('login.html', data="test")
    
@bp.route('/sign_in')
def sign_in():
    return render_template('sign_in.html')

@bp.route('/list')
@require_access_token
def list(decode_token):
    page = request.args.get('page', 1, type=int)
    users = db.jungle.find({}, {"_id": 0, "user_pw": 0}).skip((page-1) * PAGE_SIZE).limit(PAGE_SIZE)
    total_count = db.jungle.count_documents({})
    last_page_num = math.ceil(total_count / PAGE_SIZE)
    user_list = [user for user in users]
    data = {"user_list" : user_list, "last_page_num" : last_page_num}

    return render_template('list.html', data=data)



# @bp.route('/get_user')
# def get_user():
#     return render_template('get_user.html')

@bp.route('/quiz')
def quiz():
    return render_template('quiz.html')

@bp.route('/result')
def result():
    return render_template('result.html')