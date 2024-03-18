import hashlib

from bson import ObjectId
from flask import Flask, jsonify, request
from flask_jwt_extended import *
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.jungle

admin_id = "1234"
admin_pw = "qwer"

app = Flask(__name__)

@app.route('/')
def home():
   return 'hello flask!'


@app.route('/sign_in', methods=['POST'])
def api_regoster():

   user_id = request.form['id']
   user_pw = request.form['pw']
   user_name = request.form['name']

   pw_hash = hashlib.sha256(user_pw.encode('utf-8')).hexdigest()

   find_one = db.jungle.find_one({'user_id': user_id})
   print(find_one)

   if find_one is None:

      db.jungle.insert_one({"user_id" : user_id, "user_pw" : pw_hash, "user_name" : user_name})
      return jsonify({"status": "success"})

   # 로그인 실패 로직
   return jsonify({"status" : "error", "errormsg" : "User already exists"})



@app.route('/login', methods=['POST'])
def login_proc():

   input_data = request.get_json()
   user_id = input_data['id']
   user_pw = input_data['pw']

   if (user_id == admin_id and
           user_pw == admin_pw):
      return jsonify(
         result="success",
         # 검증된 경우, access 토큰 반환
         access_token=create_access_token(identity=user_id,
                                          expires_delta=False)
      )

   # 아이디, 비밀번호가 일치하지 않는 경우
   else:
      return jsonify(
         result="Invalid Params!"
      )


if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)