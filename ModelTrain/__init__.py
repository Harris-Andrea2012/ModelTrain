import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
ENVIRON = os.environ.get('ENV')

from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


app = Flask(__name__)

SECRET = os.environ.get('SECRET_KEY')

app.secret_key = SECRET


if ENVIRON == 'dev':
    app.debug = True
    DB_USER= os.environ.get('DB_USER_DEV')
    DB_PASSWORD= os.environ.get('DB_PASSWORD_DEV')
else:
    app.debug = False
    DB_USER= os.environ.get('DB_USER_DEPLOY')
    DB_PASSWORD= os.environ.get('DB_PASSWORD_DEPLOY')

#Will have to fix the localhost variable later
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{0}:{1}@localhost/ModelTrain'.format(DB_USER, DB_PASSWORD)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


csrf = CSRFProtect(app)
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'signUp'
login_manager.refresh_view = 'login'
login_manager.needs_refresh_message = (
    u"To protect your account, please reauthenticate to access this page."
)

UPLOAD_FOLDER = 'static/uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'csv'}
from ModelTrain import routes