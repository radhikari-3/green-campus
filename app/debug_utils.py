import datetime
from app import db
from app.models import User
from app.logger import logger as log
from sqlalchemy import text

def reset_db():
<<<<<<< HEAD

=======
    """ Drop all tables and seed five verified demo users. """
>>>>>>> a06ace9ab5fa065ed798c1be2b9dd748e5adcee4
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
<<<<<<< HEAD
        user = User(**u, email_verified=True)
=======
        user = User(**u)
>>>>>>> a06ace9ab5fa065ed798c1be2b9dd748e5adcee4
        user.set_password(pw)
        db.session.add(user)
    db.session.commit()

