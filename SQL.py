from models import *
class SQL():
    def __init__(self, db):
        self.db = db
    def get_all_user(self):
        return self.db.session.query(User.user_id, User.password, User.token).all()

    def get_token_by_id(self, id):
        return self.db.session.query(User).filter(User.user_id==id).first().token

    def confirm_login(self, id, pw):
        try:
            self.db.session.query(User).filter(User.email == id, User.password == pw)
            return True
        except:
            return False