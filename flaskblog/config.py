import os

class Config:
    MAIL_PORT= 587
    MAIL_USE_TLS = True
    MAIL_SERVER = 'smtp.office365.com'
    SECRET_KEY = os.environ.get('FLASKBLOG_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('PYMYSQL_TEST_URI')   
    MAIL_USERNAME = os.environ.get('MAIL_OFFICE365_USER')
    MAIL_PASSWORD = os.environ.get('MAIL_OFFICE365_PASSWORD')
    FLASK_ADMIN_SWATCH = 'cerulean'