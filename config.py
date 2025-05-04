from dotenv import load_dotenv

import os

# Load environment variables from .flaskenv
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or b'WR#&f&+%78er0we=%799eww+#7^90-;s'
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'data', 'uploads')
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ECHO = True

    # Rohit's config
    # SQLALCHEMY_DATABASE_URI = 'postgresql://local:admin@localhost/postgres'

    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:password@localhost/postgres'

    # SQLALCHEMY_ECHO = False
    # SQLALCHEMY_DATABASE_URI = f"postgresql://{os.environ.get('DB_USERNAME', 'default_user')}:{os.environ.get('DB_PASSWORD', 'default_password')}@localhost/{os.environ.get('DB_NAME', 'default_db')}"

