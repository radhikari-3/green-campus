# === Flask Extension Instances ===

from flask_apscheduler import APScheduler  # For scheduling background jobs
from flask_login import LoginManager       # For handling user sessions and authentication
from flask_mail import Mail                # For sending emails through Flask
from flask_sqlalchemy import SQLAlchemy    # ORM for database models

# Initialize Flask extensions (to be bound later in create_app)
db = SQLAlchemy()           # Database instance
login = LoginManager()      # Login/session manager
mail = Mail()               # Email handler
scheduler = APScheduler()   # Job scheduler for recurring tasks
