from flask import Flask, request, render_template

app = Flask(__name__)
app.debug = True
###################### DB ############################
import os
from models import *
from FCMController import *
import sqlite3 as sql3
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
        except :
            db.session.rollback()
            return {'code': 204,
                    'success': 'register failed'}



@api.route('/login')
class Login(Resource):
    def post(self):
        user_id = request.form['user_id']
        print(user_id)
        password = request.form['password']
        print(password)
        new_token = request.form['token']
        print(new_token)

        # 토큰 정보 갱신
        cur_token = sql.get_token_by_id(user_id)
        token_changed = False
        if new_token != cur_token:
            user = User.query.filter(User.user_id == user_id).first()
            user.token = new_token
            db.session.flush()
            db.session.commit()
            token_changed = True

        if sql.confirm_login(user_id, password):
            return {'code': 200,
                    'success': f'login successful, new_token:{token_changed}'}
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
        elif response == 'cancel':
            # 상대방에게 FCM 날려서 액티비티 종료시키기
            fcm.cancel_call(user_id, counter_token)
            return {'code': 202,
                    'success': 'propose_call canceled'}
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

@api.route('/cancel_call')
class CancelCall(Resource):
    def post(self):
        user_id = request.form['user_id']
        chatManager.set_cancel(user_id)
        return {'code': 200,
                'success': 'response_call successful'}


@api.route('/get_book')
class GetBook(Resource):
    def post(self):
        user_id = request.form['user_id']
        books = sql.get_books_by_id(user_id)
        result = [{'counter_id': counter_id,
                  'name': name,
                  'bookmark': bookmark} for counter_id, name, bookmark in books]

        if len(result) == 0:
            return {'code': 201,
                    'result': result}

        return {'code': 200,
                'result': result}

@api.route('/get_bookmark')
class GetBookmark(Resource):
    def post(self):
        user_id = request.form['user_id']
        books = sql.get_bookmark_by_id(user_id)
        result = [{'counter_id': counter_id,
                  'name': name,
                  'bookmark': bookmark} for counter_id, name, bookmark in books]

        if len(result) == 0:
            return {'code': 201,
                    'result': result}

        return {'code': 200,
                'result': result}

@api.route('/add_book')
class AddBook(Resource):
    def post(self):
        user_id = request.form['user_id']
        counter_id = request.form['counter_id']
        name = request.form['name']

        book = Book(user_id=user_id, counter_id=counter_id, name=name)

        try:
            db.session.add(book)
            db.session.commit()
            return {'code': 200,
                    'success': 'add_book successful'}
        except Exception as e:
            print(e.args)
            db.session.rollback()
            return {'code': 201,
                    'success': 'add_book failed'}




@api.route('/edit_book')
class EditBook(Resource):
    def post(self):
        user_id = request.form['user_id']
        counter_id = request.form['counter_id']
        counter_name = request.form['name']

        counter_user = Book.query.filter(Book.user_id == user_id, Book.counter_id == counter_id).first()
        counter_user.name = counter_name
        try:
            db.session.flush()
            db.session.commit()
        except Exception as e:
            print(e.args)
            db.session.rollback()
            return {'code': 201,
                    'success': 'edit_book failed'}

        return {'code': 200,
                'success': 'edit_book successful'}

@api.route('/edit_bookmark')
class EditBookmark(Resource):
    def post(self):
        user_id = request.form['user_id']
        counter_id = request.form['counter_id']
        bookmark = request.form['bookmark'] == 'true'

        counter_user = Book.query.filter(Book.user_id == user_id, Book.counter_id == counter_id).first()
        counter_user.is_marked = not counter_user.is_marked

        try:
            db.session.flush()
            db.session.commit()
        except Exception as e:
            print(e.args)
            db.session.rollback()
            return {'code': 201,
                    'success': 'edit_bookmark failed'}

        return {'code': 200,
                'success': 'edit_book successful'}


@app.route('/users')
def users():
    return render_template("users.html", result=sql.get_all_users())

@app.route('/books')
def books():
    return render_template("books.html", result=sql.get_all_books())


@app.route("/")
def index():
    return "<h1>Hello!</h1>"


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
