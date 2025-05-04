import threading

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask import Flask
from jinja2 import StrictUndefined

from app.extensions import db, login, mail
from app.logger import logger
#from app.stepsdata_simulator import run_steps_simulator
from app.views.auth import auth_bp
from app.views.main import main_bp
from app.views.user_dashboard import user_dash_bp
from config import Config

app = Flask(__name__)
app.jinja_env.undefined = StrictUndefined
app.config.from_object(Config)
db.init_app(app)
login.login_view = 'login'
login.init_app(app)
mail.init_app(app)

#Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)

app.register_blueprint(user_dash_bp)

from app import views, models
from app.debug_utils import reset_db

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, sa=sa, so=so, reset_db=reset_db)

from app.iot_simulator import simulator_thread

first_request_handled = False

# Start a background thread when Flask starts
@app.before_request
def activate_simulator():
    global first_request_handled
    if not first_request_handled:
        first_request_handled = True
        thread = threading.Thread(target=simulator_thread)
        thread.daemon = True
        thread.start()

        #with app.app_context():
        #    run_steps_simulator()