from flask_migrate import Migrate
from app import app, db  # adjust based on your project structure

migrate = Migrate(app, db)