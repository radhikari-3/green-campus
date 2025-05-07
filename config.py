from dotenv import load_dotenv
import os

# === Load Environment Variables ===
# Automatically loads variables from .flaskenv or .env file into the environment
load_dotenv()

# Base directory of the project
basedir = os.path.abspath(os.path.dirname(__file__))

# === Flask Application Configuration ===
class Config:
    # Secret key used for session management, CSRF protection, etc.
    SECRET_KEY = os.environ.get('SECRET_KEY') or b'WR#&f&+%78er0we=%799eww+#7^90-;s'

    # Path to store uploaded files
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'data', 'uploads')

    # Maximum file upload size (1 MB)
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024

    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable event system to save memory
    SQLALCHEMY_ECHO = False

    # Database URI constructed from environment variables
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{os.environ.get('DB_USERNAME', 'default_user')}:"
        f"{os.environ.get('DB_PASSWORD', 'default_password')}@localhost/"
        f"{os.environ.get('DB_NAME', 'default_db')}"
    )

    # === Email / Mail Settings (SendGrid via SMTP) ===
    MAIL_SERVER = 'smtp.sendgrid.net'  # SendGrid SMTP server
    MAIL_PORT = 587                    # TLS port
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'apikey'
    MAIL_PASSWORD = os.environ.get('SENDGRID_API_KEY')  # Secret API key from env
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')  # Default sender email

    # === Background Scheduler Settings ===
    SCHEDULER_ENABLED = False      # Toggle APScheduler job activation
    SCHEDULER_TEST_NOW = False     # If True, run scheduled tasks immediately at startup

    # === IoT Simulator Toggle ===
    IOT_SIMULATOR_ACTIVE = False   # Toggle for simulated energy sensor data generation
