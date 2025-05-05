from flask_apscheduler import APScheduler
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login = LoginManager()
mail = Mail()
scheduler = APScheduler()