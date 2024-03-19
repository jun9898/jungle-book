import hashlib
from flask import Flask, jsonify, request
from route import bp
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
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


@app.route('/login', methods=['POST'])
def login():
    user_id = request.form['user_id']
    user_pw = request.form['user_pw']

    pw_hash = hashlib.sha256(user_pw.encode('utf-8')).hexdigest()

    result = db.find_one[{'user_id': user_id, 'user_pw': pw_hash}]

    if result is not None:
        token = create_access_token(identity=user_id)
        return jsonify({"result": "success", "token": token})
    else:
        return jsonify({"result": "fail"})


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


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
