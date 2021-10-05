from flask import Flask, request

app = Flask(__name__)
app.debug = True
###################### DB ############################
import os
from models import *
from FCMController import *

fcm = FCM()
from SQL import SQL

sql = SQL(db)

basdir = os.path.abspath(os.path.dirname(__file__))
dbfile = os.path.join(basdir, 'db.sqlite')

# SQLAlchemy 설정

# 내가 사용 할 DB URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
# 비지니스 로직이 끝날때 Commit 실행(DB반영)
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
# 수정사항에 대한 TRACK
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# SECRET_KEY
app.config['SECRET_KEY'] = 'jqiowejrojzxcovnklqnweiorjqwoijroi'

db.init_app(app)
db.app = app
db.create_all()

###################### REST API ############################
from flask_restx import Api, Resource  # Api 구현을 위한 Api 객체 import

api = Api(app)  # Flask 객체에 Api 객체 등록


def on_json_loading_failed_return_dict(e):
    return {}


from ChatRoomManager import ChatRoomManaher

chatManager = ChatRoomManaher()


@api.route('/register')
class Register(Resource):
    def post(self):
        try:
            user_id = request.form['user_id']
            password = request.form['password']
            token = request.form['token']
            user = User(user_id=user_id, password=password, token=token)
            db.session.add(user)
            db.session.commit()
            return {'code': 200,
                    'success': 'register successful'}
        except:
            return {'code': 204,
                    'success': 'register failed'}


@api.route('/login')
class Login(Resource):
    def post(self):
        user_id = request.form['user_id']
        password = request.form['password']
        if sql.confirm_login(user_id, password):
            return {'code': 200,
                    'success': 'login successful'}
        else:
            return {'code': 204,
                    'success': 'login failed'}


@api.route('/propose_call')
class ProposeCall(Resource):
    def post(self):
        user_id = request.form['user_id']
        counter_id = request.form['counter_id']
        counter_token = sql.get_token_by_id(counter_id)

        # FCM
        room_num = chatManager.make_room(user_id, counter_id)
        fcm.propose_call(user_id, room_num, counter_token)
        response = chatManager.wait_accept(user_id, counter_id, room_num)
        print(f'{user_id}로부터 {counter_id}로의 전화가 {response}되었습니다.')
        if response == 'active':
            return {'code': 200,
                    'room_num': room_num,
                    'success': 'propose_call successful'}
        elif response == 'reject':
            return {'code': 201,
                    'success': 'propose_call rejected'}
        else:
            return {'code': 204,
                    'success': 'propose_call timeout'}


@api.route('/response_call')
class ResponseCall(Resource):
    def post(self):
        user_id = request.form['user_id']
        response = request.form['response']
        print(response)
        chatManager.set_accept(user_id, response)
        return {'code': 200,
                'success': 'response_call successful'}


# @api.route('/quit_call')
# class QuitCall(Resource):
#     def post(self):
#         user_id = request.form['user_id']
#         counter_id = request.form['counter_id']
#         chatManager.set_accept(user_id)
#         return {'code': 200,
#                 'success': 'accept_call successful'}
#

@app.route("/")
def index():
    return "<h1>Hello!</h1>"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)