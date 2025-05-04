import datetime
from app import db
from app.models import User
from app.logger import logger as log
from sqlalchemy import text

from app.stepsdata_simulator import run_steps_simulator


def reset_db():
    """ Drop all tables and seed five verified demo users. """

    db.drop_all()
    db.create_all()

    users = [
        {'email': 'amy@b.com', 'role': 'Admin', 'pw': 'amy.pw'},
        {'email': 'tom@b.com', 'pw': 'amy.pw'},
        {'email': 'yin@b.com', 'role': 'Admin', 'pw': 'amy.pw'},
        {'email': 'trq@b.com', 'pw': 'amy.pw'},
        {'email': 'jo@b.com', 'pw': 'amy.pw'},
        {'email': 'nairvishwa24998@gmail.com', 'pw': 'amy.pw'}
    ]

    for u in users:
        pw = u.pop('pw')
        user = User(**u, email_verified=True)
        user.set_password(pw)
        db.session.add(user)

    db.session.commit()
    log.info("Database reset and seeded with demo users.")
