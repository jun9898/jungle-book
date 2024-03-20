import math
from flask import Blueprint, jsonify, render_template, request
from database import db
from decorator import require_access_token

bp = Blueprint('routes', __name__)

CONTENT_SIZE = 6
PAGE_SIZE = 5


@bp.route('/')
def home():
    query = [
        {'$sample': {'size': 10}},
        {'$project': {'_id': 0, 'user_id': 1, 'user_name': 1,
                      'user_profile': 1}}
    ]
    random_users = db.jungle.aggregate(query)
    users = [user for user in random_users]
    return render_template('index.html', data=users)


@bp.route('/login')
def login():
    return render_template('login.html', data="test")


@bp.route('/sign_in')
def sign_in():
    return render_template('sign_in.html')


@bp.route('/list')
@require_access_token
def list(decode_token):

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

    users = db.jungle.find({}, {"_id": 0, "user_pw": 0}).skip(
        (cur_page-1) * CONTENT_SIZE).limit(CONTENT_SIZE)
    user_list = [user for user in users]
    data = {"user_list": user_list, "start_page": start_page,
            "page_list": page_list, "cur_page": cur_page}

    print("total_page", total_page)
    print("cur_page", cur_page)
    print("page_list", page_list)
    print("start_page", start_page)

    return render_template('list.html', data=data)


@bp.route('/quiz')
@require_access_token
def quiz(token):
    return render_template('quiz.html')


@bp.route('/result')
@require_access_token
def result(token):
    score = request.args.get("score")
    max_count = request.args.get("max_count")

    # 사용자 데이터 조회
    user = db.jungle.find_one({'user_id': token})

    existing_score = user.get('score')

    if existing_score:
        if int(existing_score) < int(score):
            db.jungle.update_one(
                {'user_id': token},
                {'$set': {'score': score}}
            )
    else:
        db.jungle.update_one(
            {'user_id': token},
            {'$set': {'score': score}}
        )

    data = {"score": score, "max_count": max_count}
    return render_template('result.html', data=data)


@bp.route('/profile')
@require_access_token
def profile(token):
    global check_mypage
    check_mypage = False
    user_id = request.args.get("user_id")
    user = db.jungle.find_one({"user_id": user_id}, {
                              "_id": 0, "user_id": 1, "user_profile": 1, "score": 1, "user_name" : 1})
    user_score = user.get("score")

    if user_score:
        high_score = user_score

    if token == user_id:
        check_mypage = True

    if user:
        if user_score:
            data = {"user": user, "check_mypage": check_mypage,
                    "score": high_score}
        else:
            data = {"user": user, "check_mypage": check_mypage}
        return render_template('profile.html', data=data)

@bp.route('/mypage')
@require_access_token
def mypage(token):
    check_mypage = True
    user = db.jungle.find_one({"user_id": token}, {
        "_id": 0, "user_id": 1, "user_profile": 1, "score": 1, "user_name": 1})
    user_score = user.get("score")

    if user_score:
        high_score = user_score

    if user:
        if user_score:
            data = {"user": user, "check_mypage": check_mypage,
                    "score": high_score}
        else:
            data = {"user": user, "check_mypage": check_mypage}
        return render_template('profile.html', data=data)
