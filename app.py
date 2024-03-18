import datetime
import hashlib

from flask import Flask, jsonify, request

from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from pymongo import MongoClient
from secret_key import SECRET_KEY
client = MongoClient('localhost', 27017)
db = client.jungle

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = SECRET_KEY
jwt = JWTManager(app)


@app.route('/')
def home():
   return 'hello flask!'


@app.route('/sign_in', methods=['POST'])
def api_register():

   user_id = request.form['user_id']
   user_pw = request.form['user_pw']
   user_name = request.form['user_name']

   pw_hash = hashlib.sha256(user_pw.encode('utf-8')).hexdigest()

   find_one = db.jungle.find_one({'user_id': user_id})

   if find_one is None:
      db.jungle.insert_one(
         {"user_id": user_id, "user_pw": pw_hash, "user_name": user_name})
      return jsonify({"status": "success"})

   # 로그인 실패 로직
   return jsonify({"status": "error", "errormsg": "User already exists"})


@app.route('/login', methods=['POST'])
def login():
   user_id = request.form['user_id']
   user_pw = request.form['user_pw']

   pw_hash = hashlib.sha256(user_pw.encode('utf-8')).hexdigest()

   find_one = db.find_one[{'user_id': user_id, 'user_pw': pw_hash}]

   if find_one is not None:
      token = create_access_token(identity=user_id)
      return jsonify({"result": "success", "token": token})
   else:
      return jsonify({"result": "fail"})


@app.route('/login_test', methods=['GET'])
@jwt_required()
def login_test():
   return jsonify({"result": "success"})


if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)
