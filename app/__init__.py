from flask import Flask
from config import Config
from flask_mysqldb import MySQL
from flask_login import LoginManager
from flask_mail import Mail

# Create all the models
app=Flask(__name__)
app.config.from_object(Config)
mysql=MySQL(app)
mail = Mail(app)

from app import routes
