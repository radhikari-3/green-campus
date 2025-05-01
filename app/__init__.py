import threading

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from jinja2 import StrictUndefined

from app.logger import logger
from config import Config

app = Flask(__name__)
app.jinja_env.undefined = StrictUndefined
app.config.from_object(Config)
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'


from app import views, models
from app.debug_utils import reset_db

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, sa=sa, so=so, reset_db=reset_db)


from app.iot_simulator import simulator_thread

first_request_handled = False

# Start background thread when Flask starts
@app.before_request
def activate_simulator():
    global first_request_handled
    if not first_request_handled:
        first_request_handled = True
        thread = threading.Thread(target=simulator_thread)
        thread.daemon = True
        thread.start()