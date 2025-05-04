import datetime
from app import db
from app.models import User
from app.logger import logger as log
from app.stepsdata_simulator import run_steps_simulator
from sqlalchemy import text

def reset_db():
    """ Drop all tables and seed verified demo users. """
    db.drop_all()
    db.create_all()

    users = [
        {'email': 'amy@b.com', 'role': 'Admin', 'pw': 'amy.pw'},
        {'email': 'tom@b.com', 'pw': 'amy.pw'},
        {'email': 'yin@b.com', 'role': 'Admin', 'pw': 'amy.pw'},
        {'email': 'trq@b.com', 'pw': 'amy.pw'},
        {'email': 'jo@b.com', 'pw': 'amy.pw'},
        {'email': 'yashzore321@gmail.com', 'pw': 'amy.pw'}
    ]

    for u in users:
        pw = u.pop('pw')
        u.pop('role', None)  # Remove 'role' if present

        user = User(**u)
        user.set_password(pw)
        user.email_verified = True
        db.session.add(user)

    db.session.commit()

    #run_steps_simulator()
