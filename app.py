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


PAGE_LIMIT = 10

@app.route('/')
def home():
   return 'hello flask!'


@app.route('/sign_in', methods=['POST'])
def api_register():

   user_id = request.form['user_id']
   user_pw = request.form['user_pw']
   user_name = request.form['user_name']

   pw_hash = hashlib.sha256(user_pw.encode('utf-8')).hexdigest()

   result = db.jungle.find_one({'user_id': user_id})

   if result is None:
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

   result = db.find_one[{'user_id': user_id, 'user_pw': pw_hash}]

   if result is not None:
      token = create_access_token(identity=user_id)
      return jsonify({"result": "success", "token": token})
   else:
      return jsonify({"result": "fail"})


@app.route('/list', methods=['GET'])
@jwt_required()
def list():
   page = int(request.args.get("page"))
   offset  = (page - 1) * PAGE_LIMIT
   users = db.jungle.find({}, {"_id": 0}).limit(PAGE_LIMIT).skip(offset)
   user_list = [user for user in users]
   return jsonify({"result": "success", "users": user_list})


@app.route('/profile', methods=['GET'])
@jwt_required()
def getProfile():
   user_id = request.form['user_id']
   user = db.jungle.find_one({'user_id': user_id}, {"_id": 0})
   return jsonify({"result": "success", "user": user})


if __name__ == '__main__':
   app.run('0.0.0.0', port=5001, debug=True)
