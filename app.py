import hashlib
from flask import Flask, jsonify, request, render_template
from route import bp
from flask_jwt_extended import JWTManager, create_refresh_token, create_access_token, get_jwt_identity, jwt_required, \
    set_access_cookies, set_refresh_cookies
from secret_key import SECRET_KEY
from database import db

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = SECRET_KEY
app.register_blueprint(bp)
jwt = JWTManager(app)

PAGE_LIMIT = 10

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
    save_path = './profile/' + file.filename
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
        resp = jsonify({'login': True})
        set_access_cookies(resp, access_token)
        set_refresh_cookies(resp, refresh_token)
        return resp, 200
    else:
        response = jsonify({"error": "로그인에 실패했습니다."})
        response.status_code = 401  # Unauthorized
        return response


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

@app.errorhandler(ValueError)
def handle_value_error(error):
    # 에러를 받아서 에러 페이지를 렌더링합니다.
    return render_template('error.html', error=error), 400


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
