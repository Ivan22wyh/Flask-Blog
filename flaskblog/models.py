from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flaskblog import db
from flaskblog import login_manager
from datetime import datetime

@login_manager.user_loader
def load_user(account_id):
	return Account.query.get(account_id)

account_subs = db.Table('user_subs',
    db.Column('following_id', db.Integer, db.ForeignKey('account.id')),
    db.Column('follower_id', db.Integer, db.ForeignKey('account.id')),
    )

post_subs = db.Table('post_subs',
    db.Column('star_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('subscriber_id', db.Integer, db.ForeignKey('account.id'))
    )

class Account(db.Model, UserMixin):

    __tablename__ = 'account'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(200), nullable=True)
    password = db.Column(db.String(200), nullable=True)
    img = db.Column(db.String(200), nullable=True, default='default.jpg')

    followings = db.relationship('Account', 
            secondary=account_subs, 
            primaryjoin=(account_subs.c.follower_id==id),
            secondaryjoin=(account_subs.c.following_id==id),
            backref=db.backref('followers', lazy='dynamic'),
            )
    
    stars = db.relationship('Post',
            secondary=post_subs,
            backref=db.backref('subscribers', lazy='dynamic')
            ) 

    messages_sent = db.relationship('Message', 
                                foreign_keys='Message.sender_id',
                                backref='author',
                                lazy='dynamic'
                                )
    messages_recieved = db.relationship('Message',
                                foreign_keys='Message.recipient_id',
                                backref='recipient',
                                lazy='dynamic'
                                )
    last_message_read_time = db.Column(db.DateTime)

    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(
            Message.timestamp > last_read_time).count()


    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Account.query.get(user_id)

class Post(db.Model):

    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=True)
    date_posted = db.Column(db.String(50), nullable=True)
    brief = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=True)
    
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    account = db.relationship("Account", backref='posts', foreign_keys=[account_id])

class Task(db.Model):

    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(200), nullable=True)
    deadline = db.Column(db.String(200), nullable=True)
    completed = db.Column(db.String(30), nullable=True)
    completed_num = db.Column(db.Integer, nullable=True)
    priority = db.Column(db.String(30), nullable=True)
    priority_num = db.Column(db.Integer, nullable=True)
    
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    account = db.relationship('Account', backref='tasks')

class Message(db.Model):

    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True)

    def __repr__(self):
        return '<Message {}>'.format(self.body)
