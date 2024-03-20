import math
from decorator import require_access_token
import hashlib
import os
import uuid

from bson import ObjectId
from flask import Flask, jsonify, redirect, request, render_template, url_for
from flask_jwt_extended import JWTManager, create_refresh_token, create_access_token, get_jwt_identity, jwt_required, \
    set_access_cookies, set_refresh_cookies, unset_jwt_cookies

from database import db
from decorator import require_access_token
from route import bp
from flask_jwt_extended import JWTManager, create_refresh_token, create_access_token, get_jwt_identity, jwt_required
from pymongo import MongoClient
from secret_key import SECRET_KEY

client = MongoClient('localhost', 27017)
db = client.jungle


app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = SECRET_KEY
app.register_blueprint(bp)
jwt = JWTManager(app)

CONTENT_SIZE = 5
PAGE_LIMIT = 10

app.config['UPLOAD_FOLDER'] = 'static/assat'

image_url = ''


@app.route('/upload_image', methods=['POST'])
def upload_image():
    image_file = request.files.get('user_profile')

    if not image_file:
        return jsonify({'result': 'fail', 'message': 'No image file found'})

    # 이미지 파일 저장 경로 설정
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], 'user_profile.jpg')
    # 이미지 파일 저장
    image_file.save(save_path)

    # 이미지 파일 URL 생성
    image_url = f'http://localhost:5000/{save_path} '
    return jsonify({'result': 'success', 'image_url': image_url})


@app.route('/sign_in', methods=['POST'])
def api_register():

    user_id = request.form['user_id']
    user = db.jungle.find_one({'user_id': user_id})

    if user:
        return jsonify({"status": "error", "message": "중복된 ID입니다."})

    user_pw = request.form['user_pw']
    user_name = request.form['user_name']

    if 'user_profile' not in request.files:
        return jsonify({"error": "No file part"})
    file = request.files['user_profile']
    if file.filename == "":
        return jsonify({"error": "No selected file"})
    file_extension = file.filename.split('.')[-1]  # 파일 확장자 추출
    uuid_filename = str(uuid.uuid4()) + '.' + \
        file_extension  # UUID를 포함한 새로운 파일 이름 생성

    # 파일 저장 경로 설정
    save_path = './static/profile/' + uuid_filename
    file.save(save_path)

    pw_hash = hashlib.sha256(user_pw.encode('utf-8')).hexdigest()

    db.jungle.insert_one(
        {"user_id": user_id, "user_pw": pw_hash, "user_name": user_name, "user_profile": uuid_filename})
    return jsonify({"status": "success"})


@app.route('/user-login', methods=['POST'])
def login():
    user_id = request.form['user_id']
    user_pw = request.form['user_pw']

    pw_hash = hashlib.sha256(user_pw.encode('utf-8')).hexdigest()

    result = db.jungle.find_one({'user_id': user_id, 'user_pw': pw_hash})

    if result is not None:
        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)
        resp = jsonify({'login': True})
        set_access_cookies(resp, access_token)
        set_refresh_cookies(resp, refresh_token)
        return resp, 200
    else:
        response = jsonify({"error": "로그인에 실패했습니다."})
        response.status_code = 401  # Unauthorized
        return response


@app.route('/logout', methods=['POST'])
def logout():
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    return resp, 200


@app.route('/get_user', methods=['GET'])
@require_access_token
def get_user(token):
    find_user_id = request.args.get("user_id")
    page = request.args.get("page", type=int)
    print(page)

    # 각 페이지의 첫 번째 인덱스 계산
    skip_count = (page - 1) * CONTENT_SIZE

    # 사용자 데이터 조회
    user = db.jungle.find_one({'user_id': find_user_id}, {
                              "_id": 0, "comments": 1})

    # 댓글 데이터 조회
    comments = user.get("comments", [])
    comments = comments[::-1]
    comments_count = len(comments)

    # 페이지에 맞게 댓글 데이터를 자르기
    start_index = skip_count
    end_index = min(skip_count + CONTENT_SIZE, comments_count)
    paginated_comments = comments[start_index:end_index]

    # 페이징 여부 확인
    last_page = math.ceil(comments_count / CONTENT_SIZE)
    check_last_page = page >= last_page

    # 페이징된 사용자 데이터 및 페이징 정보 반환

    data = {"check_last_page": check_last_page,
            "comments": list(paginated_comments)}

    return jsonify({"result": "success", "data": data})


@app.route('/add_comment', methods=['POST'])
@require_access_token
def add_comment(token):
    user_id = request.form['user_id']
    login_user = token
    login_user_info = db.jungle.find_one(
        {'user_id': login_user}, {'comments': 0, '_id': 0, 'user_pw': 0})
    comment_text = request.form['comment']

    comment = {
        'writter': login_user_info,
        'comment': comment_text
    }

    db.jungle.update_one(
        {'user_id': user_id},
        {'$push': {'comments': comment}}
    )

    # 프로필 페이지로 리다이렉트하여 새로고침을 유도
    return redirect(url_for('routes.profile', user_id=user_id))


@app.errorhandler(ValueError)
def handle_value_error(error):
    # 에러를 받아서 에러 페이지를 렌더링합니다.
    return render_template('error.html', error=error), 400


@app.route('/random_users', methods=['GET'])
@require_access_token
def quiz(token):
    query = [
        {'$sample': {'size': 10}},
        {'$project': {'_id': 0, 'user_id': 1, 'user_name': 1,
                      'user_profile': 1}}
    ]
    random_users = db.jungle.aggregate(query)
    users = [user for user in random_users]
    return jsonify({"result": "success", "users": users})


@app.route('/score', methods=['POST'])
@require_access_token
def score(token):
    score = request.form['score']
    return jsonify({"result": "success", "score": score})


@app.errorhandler(ValueError)
def handle_value_error(error):
    # 에러를 받아서 에러 페이지를 렌더링합니다.
    return render_template('error.html', error=error), 400


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
