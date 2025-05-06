import threading

import sqlalchemy as sa
import sqlalchemy.orm as so
from apscheduler.triggers.cron import CronTrigger
from flask import Flask
from jinja2 import StrictUndefined

import config
from app.extensions import db, login, mail, scheduler
from app.logger import logger
from app.logger import logger
from app.tasks import scheduled_send_discount_email
from app.views.auth import auth_bp
from app.views.dashboard import dash_bp
from app.views.energy_dashboard import energy_bp
from app.views.main import main_bp
from app.views.smart_expiry_dashboard import smart_exp_bp
from app.views.vendor_dashboard import vendors_bp
from config import Config
first_request_handled = False


app = Flask(__name__)
app.jinja_env.undefined = StrictUndefined
app.config.from_object(Config)

db.init_app(app)
login.login_view = 'auth.login'
login.init_app(app)
mail.init_app(app)

#Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)

app.register_blueprint(dash_bp)

from app import views, models           # don't remove from here
from app.debug_utils import reset_db    # don't remove from here

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, sa=sa, so=so, reset_db=reset_db)



first_request_handled = False


def create_app(config_class=Config, test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    app.jinja_env.undefined = StrictUndefined

    db.init_app(app)
    login.login_view = 'auth.login'
    login.init_app(app)
    mail.init_app(app)

    #Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(dash_bp)

    #app.register_blueprint(utils_bp)
    app.register_blueprint(smart_exp_bp)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(energy_bp)

    # Setup scheduler
    if app.config.get('SCHEDULER_ENABLED', True):
        scheduler.start()
        logger.info("Scheduler has started.")
        scheduler.add_job(
            func=scheduled_send_discount_email,
            trigger=CronTrigger(hour=7, minute=0),
            id='daily_discount_email',
            replace_existing=True
        )
        logger.info("Scheduled daily_discount_email job for 7 AM.")
    else:
        logger.info("Scheduler is disabled because SCHEDULER_ENABLED is set to False.")


    # Optional: trigger immediately on startup
    if app.config.get('SCHEDULER_TEST_NOW', False):
        with app.app_context():
            scheduled_send_discount_email()

    from app import views, models           # don't remove from here
    from app.debug_utils import reset_db    # don't remove from here

    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, sa=sa, so=so, reset_db=reset_db)


    from app.iot_simulator import simulator_thread # don't remove from here
    # Start a background thread when Flask starts
    @app.before_request
    def activate_simulator():
        global first_request_handled
        if not first_request_handled and not app.config.get('TESTING', False):
            first_request_handled = True
            thread = threading.Thread(target=simulator_thread, args=(app,))  # Pass app to simulator_thread
            thread.daemon = True
            thread.start()

    return app