import os

import threading
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from jinja2 import StrictUndefined

from config import Config

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret!'
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_PASSWORD'] = os.environ.get('SENDGRID_API_KEY')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

mail = Mail(app)

app.jinja_env.undefined = StrictUndefined
app.config.from_object(Config)

db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'

from app.debug_utils import reset_db
from app.logger import logger
from app.views import scheduler

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, sa=sa, so=so, reset_db=reset_db)

from app.iot_simulator import simulator_thread

first_request_handled = False

@app.before_request
def activate_simulator():
    global first_request_handled
    if not first_request_handled:
        first_request_handled = True
        thread = threading.Thread(target=simulator_thread)
        thread.daemon = True
        thread.start()

        from app.stepsdata_simulator import run_steps_simulator
        if app.config.get('ENABLE_SIMULATOR', False):
            with app.app_context():
                run_steps_simulator()

#
from app import views


def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        print("Scheduler started!")

# Initialize the scheduler
start_scheduler()