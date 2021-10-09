from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKeyConstraint

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.String(32), primary_key=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    token = db.Column(db.String(256), nullable=False)


class Book(db.Model):
    __tablename__ = 'book'
    user_id = db.Column(db.String(32), primary_key=True, nullable=False)
    counter_id = db.Column(db.String(32), primary_key=True, nullable=False)
    name = db.Column(db.String(32), nullable=False, default=counter_id)
    is_marked = db.Column(db.Boolean(), nullable=False, default=False)

    __table_args__ = (ForeignKeyConstraint((user_id, counter_id),
                                           [User.user_id, User.user_id]), {})
