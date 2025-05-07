from dotenv import load_dotenv
import os

# === Load Environment Variables ===
# Load key-value pairs from a .flaskenv or .env file into os.environ
load_dotenv()

# === Base Directory Setup ===
# Used to build absolute paths for file storage
basedir = os.path.abspath(os.path.dirname(__file__))

# === Flask App Configuration Class ===
class Config:
    # Secret key used for sessions and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or b'WR#&f&+%78er0we=%799eww+#7^90-;s'

    # Path to store uploaded files (e.g., product images, documents)
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'data', 'uploads')

    # Limit upload size to 1 MB
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024

    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable modification tracking (improves performance)
    SQLALCHEMY_ECHO = False

    # Database URI constructed from environment variables
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{os.environ.get('DB_USERNAME', 'default_user')}:"
        f"{os.environ.get('DB_PASSWORD', 'default_password')}@localhost/"
        f"{os.environ.get('DB_NAME', 'default_db')}"
    )

    # === Email (SendGrid SMTP) Configuration ===
    MAIL_SERVER = 'smtp.sendgrid.net'         # SMTP server for SendGrid
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'apikey'
    MAIL_PASSWORD = os.environ.get('SENDGRID_API_KEY')  # SendGrid API Key from env
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')  # Default 'from' address

    # === Scheduler Flags (APScheduler) ===
    SCHEDULER_ENABLED = os.environ.get('SCHEDULER_ENABLED')        # Enable/disable cron jobs
    SCHEDULER_TEST_NOW = os.environ.get('SCHEDULER_TEST_NOW')      # Run jobs on startup if True

    # === IoT Simulator Toggle ===
    IOT_SIMULATOR_ACTIVE = os.environ.get('IOT_SIMULATOR_ACTIVE')  # Toggle simulator for energy data
