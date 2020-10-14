import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flaskblog.config import Config
from flaskblog.admin import (MyAdminIndexView, MyUserView, MyTaskView,
                         MyPostView, MyMessageView, CustomFileAdmin)

path = os.path.join(os.path.dirname(__file__), 'static')

bcrypt = Bcrypt()
mail = Mail()
db = SQLAlchemy()
login_manager = LoginManager()
admin = Admin(name='Admin', index_view=MyAdminIndexView())

from flaskblog.models import Account, Post, Task, Message

login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'
login_manager.refresh_view = "accounts.reauthenticate"
login_manager.needs_refresh_message = (
u"To protect your account, please reauthenticate to access this page."
)
login_manager.needs_refresh_message_category = "info"

def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(Config)

    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    admin.init_app(app)

    from flaskblog.users.route import users
    from flaskblog.taskmaster.route import tasks
    from flaskblog.resources_data.route import data
    from flaskblog.main.route import main
    from flaskblog.blog.route import posts
    from flaskblog.account.route import current
    from flaskblog.account.template_filter import get_window_messages
    from flaskblog.errors.handlers import errors

    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(tasks)
    app.register_blueprint(data)
    app.register_blueprint(main)
    app.register_blueprint(current)
    app.register_blueprint(errors)
    app.add_template_filter(get_window_messages)

    admin.add_view(MyUserView(Account, db.session, category='Models'))
    admin.add_view(MyPostView(Post, db.session, category='Models'))
    admin.add_view(MyTaskView(Task, db.session, category='Models'))
    admin.add_view(MyMessageView(Message, db.session, category='Models'))
    admin.add_view(CustomFileAdmin(path, '/static/', name='Static Files'))
    
    return app
    



















