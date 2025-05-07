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

# Flag to ensure IoT simulator only runs once
first_request_handled = False

def create_app(config_class=Config, test_config=None):
    # Initialize Flask app with default config
    app = Flask(__name__)
    app.config.from_object(Config)

    # If a test config is passed, override the defaults
    if test_config:
        app.config.update(test_config)

    # Raise errors if undefined variables are used in Jinja templates
    app.jinja_env.undefined = StrictUndefined

    # Initialize extensions
    db.init_app(app)
    login.login_view = 'auth.login'
    login.init_app(app)
    mail.init_app(app)

    # Register Blueprints for different parts of the app
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(dash_bp)
    app.register_blueprint(smart_exp_bp)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(energy_bp)

    # Setup the background scheduler if enabled
    if app.config.get('SCHEDULER_ENABLED', True):
        scheduler.start()
        logger.info("Scheduler has started.")

        # Schedule the daily email task at 7:00 AM
        scheduler.add_job(
            func=scheduled_send_discount_email,
            trigger=CronTrigger(hour=7, minute=0),
            id='daily_discount_email',
            replace_existing=True
        )
        logger.info("Scheduled daily_discount_email job for 7 AM.")
    else:
        logger.info("Scheduler is disabled because SCHEDULER_ENABLED is set to False.")

    # Optional: Run scheduled email task immediately at startup (useful for testing)
    if app.config.get('SCHEDULER_TEST_NOW', False):
        with app.app_context():
            scheduled_send_discount_email()

    # Import views and models to ensure routes and tables are registered
    from app import views, models  # don't remove
    from app.debug_utils import reset_db  # don't remove

    # Make some objects available in the Flask shell for easy access
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, sa=sa, so=so, reset_db=reset_db)

    # IoT simulator import and background thread setup
    from app.iot_simulator import simulator_thread  # don't remove

    # Start IoT simulator thread on the first request (not during testing)
    @app.before_request
    def activate_simulator():
        global first_request_handled
        if not first_request_handled and not app.config.get('TESTING', False):
            first_request_handled = True
            if app.config.get('IOT_SIMULATOR_ACTIVE', True):
                thread = threading.Thread(target=simulator_thread, args=(app,))
                thread.daemon = True  # Terminates with the main thread
                thread.start()

    return app
