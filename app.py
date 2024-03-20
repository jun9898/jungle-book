import hashlib
from flask import Flask, jsonify, request
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
    save_path = './static/profile/' + file.filename
    file.save(save_path)

    pw_hash = hashlib.sha256(user_pw.encode('utf-8')).hexdigest()

    result = db.jungle.find_one({'user_id': user_id})

    if result is None:
        db.jungle.insert_one(
            {"user_id": user_id, "user_pw": pw_hash, "user_name": user_name, "user_profile": file.filename})
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
        tokens = {'access_token': access_token, 'refresh_token': refresh_token}
        return jsonify({"result": "success", "tokens": tokens})
    else:
        response = jsonify({"error": "로그인에 실패했습니다."})
        response.status_code = 401  # Unauthorized
        return response


@app.route('/list', methods=['GET'])
@jwt_required()
def list():
    users = db.jungle.find({}, {"_id": 0})
    user_list = [user for user in users]
    return jsonify({"result": "success", "users": user_list})


@app.route('/get_user', methods=['GET'])
@jwt_required()
def get_user():
    user_id = request.form['user_id']
    user = db.jungle.find_one({'user_id': user_id}, {"_id": 0})
    return jsonify({"result": "success", "user": user})


@app.route('/add_comment', methods=['POST'])
@jwt_required()
def add_comment():
    user_id = request.form['user_id']
    login_user = get_jwt_identity()
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
# @jwt_required()
def quiz():
    query = [
        {'$sample': {'size': 10}},
        {'$project': {'_id': 0, 'user_id': 1, 'user_name': 1,
                      'user_profile': 1}}
    ]
    random_users = db.jungle.aggregate(query)
    users = [user for user in random_users]
    return jsonify({"result": "success", "users": users})


@app.route('/score', methods=['POST'])
# @jwt_required()
def score():
    score = request.form['score']
    return jsonify({"result": "success", "score": score})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
