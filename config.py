import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    MYSQL_HOST='localhost'
    MYSQL_USER='root'
    MYSQL_PASSWORD='triphopshate4254'
    MYSQL_DB='f2c'