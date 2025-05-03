import datetime
from app import db
from app.models import User
from app.logger import logger as log
from sqlalchemy import text


def reset_db():

    db.drop_all()
    db.create_all()

    users = [
        {'email': 'amy@b.com', 'role': 'Admin', 'pw': 'amy.pw'},
        {'email': 'tom@b.com', 'pw': 'amy.pw'},
        {'email': 'yin@b.com', 'role': 'Admin', 'pw': 'amy.pw'},
        {'email': 'trq@b.com', 'pw': 'amy.pw'},
        {'email': 'jo@b.com', 'pw': 'amy.pw'}
    ]

    for u in users:
        pw = u.pop('pw')
        user = User(**u, email_verified=True)
        user.set_password(pw)
        db.session.add(user)
    db.session.commit()

