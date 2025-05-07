import threading

import sqlalchemy as sa
import sqlalchemy.orm as so
from apscheduler.triggers.cron import CronTrigger
from flask import Flask
from jinja2 import StrictUndefined

from app.extensions import db, login, mail, scheduler
from app.logger import logger
from app.tasks import scheduled_send_discount_email
from app.views.auth import auth_bp
from app.views.energy_analytics import energy_bp
from app.views.food_expiry import smart_exp_bp
from app.views.main import main_bp
from app.views.user_dashboard import dash_bp
from app.views.vendor_dashboard import vendors_bp
from config import Config

# Track whether the IoT simulator has already been started
first_request_handled = False

def create_app(config_class=Config, test_config=None):
    """
    Application factory to configure and return a Flask app instance.
    """

    # === App Initialization ===
    app = Flask(__name__, template_folder='static/templates')
    app.config.from_object(Config)

    # Use test configuration if provided
    if test_config:
        app.config.update(test_config)

    # Raise errors for undefined template variables
    app.jinja_env.undefined = StrictUndefined

    # === Extension Setup ===
    db.init_app(app)
    login.login_view = 'auth.login'  # Redirect unauthorized users to login
    login.init_app(app)
    mail.init_app(app)

    # === Blueprint Registration ===
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(dash_bp)
    app.register_blueprint(smart_exp_bp)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(energy_bp)

    # === APScheduler Configuration ===
    if str(app.config.get('SCHEDULER_ENABLED', 'false')).lower() == 'true':
        scheduler.start()
        logger.info("Scheduler has started.")

        # Add daily email job at 7:00 AM
        scheduler.add_job(
            func=scheduled_send_discount_email,
            trigger=CronTrigger(hour=7, minute=0),
            id='daily_discount_email',
            replace_existing=True
        )
        logger.info("Scheduled daily_discount_email job for 7 AM.")
    else:
        logger.info("Scheduler is disabled because SCHEDULER_ENABLED is set to False.")

    # Optional: Immediately run job at startup if configured for testing
    if str(app.config.get('SCHEDULER_TEST_NOW', 'false')).lower() == 'true':
        with app.app_context():
            scheduled_send_discount_email()

    # === Shell Context Setup ===
    from app.debug_utils import reset_db    # Used for CLI shell reset

    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, sa=sa, so=so, reset_db=reset_db)

    # === IoT Simulator (Background Thread) ===
    from app.iot_simulator import simulator_thread  # Used for simulation of energy data

    @app.before_request
    def activate_simulator():
        """
        Starts the IoT simulator thread only once during the app lifecycle.
        Controlled via IOT_SIMULATOR_ACTIVE flag.
        """
        global first_request_handled
        if not first_request_handled and not str(app.config.get('IOT_SIMULATOR_ACTIVE', 'false')).lower() == 'true':
            first_request_handled = True
            if str(app.config.get('IOT_SIMULATOR_ACTIVE', 'false')).lower() == 'true':
                thread = threading.Thread(target=simulator_thread, args=(app,))
                thread.daemon = True
                thread.start()

    return app
