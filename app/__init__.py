import threading

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask import Flask
from jinja2 import StrictUndefined

from app.extensions import db, login, mail, scheduler
from app.logger import logger
from app.logger import logger
from app.tasks import send_discount_email
from app.views.auth import auth_bp
from app.views.dashboard import dash_bp
from app.views.main import main_bp
from app.views.utils import utils_bp
from app.views.vendor import vendors_bp
from config import Config


def create_app(config_class=Config, test_config=None):
    app = Flask(__name__)
    app.config.from_object(config_class)

    if test_config is not None:
        app.config.update(test_config)

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

    app.register_blueprint(utils_bp)
    app.register_blueprint(vendors_bp)

    # Setup scheduler
    scheduler.start()
    logger.info("Scheduler has started.")
    #logger.info(f"Scheduled job: {job.id}, function: {job.func_ref}, next run: {job.next_run_time}")

    # Optional: trigger immediately on startup
    if app.config.get('SCHEDULER_TEST_NOW', False):
        with app.app_context():
            send_discount_email()

    from app import views, models           # don't remove from here
    from app.debug_utils import reset_db    # don't remove from here

    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, sa=sa, so=so, reset_db=reset_db)

    first_request_handled = False

    from app.iot_simulator import simulator_thread # don't remove from here
    # Start a background thread when Flask starts
    @app.before_request
    def activate_simulator():
        global first_request_handled
        if not first_request_handled:
            first_request_handled = True
            thread = threading.Thread(target=simulator_thread)
            thread.daemon = True
            thread.start()
    return app