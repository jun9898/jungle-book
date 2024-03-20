import hashlib
import os
import uuid

from flask import Flask, jsonify, request, render_template
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
    user_pw = request.form['user_pw']
    user_name = request.form['user_name']

    if 'user_profile' not in request.files:
        return jsonify({"result": "No file part"})
    file = request.files['user_profile']
    if file.filename == "":
        return jsonify({"result": "No selected file"})
    file_extension = file.filename.split('.')[-1]  # 파일 확장자 추출
    uuid_filename = str(uuid.uuid4()) + '.' + file_extension  # UUID를 포함한 새로운 파일 이름 생성

    # 파일 저장 경로 설정
    save_path = './static/profile/' + uuid_filename
    file.save(save_path)

    pw_hash = hashlib.sha256(user_pw.encode('utf-8')).hexdigest()

    result = db.jungle.find_one({'user_id': user_id})

    if result is None:
        db.jungle.insert_one(
            {"user_id": user_id, "user_pw": pw_hash, "user_name": user_name, "user_profile": uuid_filename})
        return jsonify({"status": "success"})

    # 회원가입 실패 로직
    return jsonify({"status": "error", "errormsg": "User already exists"})


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
    user_id = token
    user = db.jungle.find_one({'user_id': user_id},
                              {"_id": 0, "user_id": 1, "user_profile": 1, "comments": 1})
    return jsonify({"result": "success", "user": user})


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

    return jsonify({"result": "success", "comment": comment})


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
