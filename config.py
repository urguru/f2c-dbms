import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    MYSQL_HOST='localhost'
    MYSQL_USER='root'
    MYSQL_PASSWORD='triphopshate4254'
    MYSQL_DB='f2c'
    SESSION_TYPE = os.environ.get('SESSION_TYPE')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['microblogteam@gmail.com']
    DEBUG=True
