import math
import jwt
from flask import Blueprint, render_template, request
from database import db
from decorator import require_access_token

bp = Blueprint('routes', __name__)

CONTENT_SIZE = 6
PAGE_SIZE = 5

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

    print(decode_token)

    page_list = []

    total_count = db.jungle.count_documents({})
    total_page = math.ceil(total_count / CONTENT_SIZE)
    cur_page = request.args.get('page', 1, type=int)
    if cur_page < 1:
        cur_page = 1
    elif cur_page > total_page:
        cur_page = total_page
    start_page = ((cur_page-1) // PAGE_SIZE) * PAGE_SIZE + 1
    if start_page + 5 < total_page:
        page_list.extend(i for i in range(start_page, start_page+5))
    else:
        page_list.extend(i for i in range(start_page, total_page+1))

    users = db.jungle.find({}, {"_id": 0, "user_pw": 0}).skip((cur_page-1) * CONTENT_SIZE).limit(CONTENT_SIZE)
    user_list = [user for user in users]
    data = {"user_list" : user_list, "start_page" : start_page, "page_list" : page_list, "cur_page" : cur_page }

    print("total_page", total_page)
    print("cur_page", cur_page)
    print("page_list", page_list)
    print("start_page", start_page)


    return render_template('list.html', data=data)


@bp.route('/quiz')
def quiz():
    return render_template('quiz.html')

@bp.route('/result')
def result():
    return render_template('result.html')