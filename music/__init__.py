from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt



app= Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db=SQLAlchemy(app)
login_manager=LoginManager()
login_manager.init_app(app)
bcrypt=Bcrypt(app)
login_manager=LoginManager(app)
login_manager.login_view='user_login'
login_manager.login_message_category = 'info'

from music import routes