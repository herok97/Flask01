from models import *


class SQL():
    def __init__(self, db):
        self.db = db

    def get_all_users(self):
        return self.db.session.query(User.user_id, User.password, User.token).all()

    def get_all_books(self):
        return self.db.session.query(Book.user_id, Book.counter_id, Book.name, Book.is_marked).all()

    def get_books_by_id(self, id):
        return self.db.session.query(Book.counter_id, Book.name, Book.is_marked).filter(Book.user_id == id).all()

    def get_token_by_id(self, id):
        return self.db.session.query(User).filter(User.user_id == id).first().token

    def confirm_login(self, id, pw):
        data = self.db.session.query(User).filter(User.user_id == id, User.password == pw).first()
        return data is not None
