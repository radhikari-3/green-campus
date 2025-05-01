#debug_utils.py
import datetime
from app import db
from app.models import User

def reset_db():
    """ Drop all tables and seed five verified demo users. """
    db.drop_all()
    db.create_all()

    demo_users = [
        {'username': 'amy',   'email': 'amy@b.com'},
        {'username': 'tom',   'email': 'tom@b.com'},
        {'username': 'yin',   'email': 'yin@b.com'},
        {'username': 'tariq', 'email': 'trq@b.com'},
        {'username': 'jo',    'email': 'jo@b.com'},
    ]

    for udata in demo_users:
        user = User(
            username=udata['username'],
            email=udata['email'],
            role='Admin',
            email_verified=True
        )
        user.signup_date = datetime.datetime.utcnow()
        user.set_password('amy.pw')
        db.session.add(user)

    db.session.commit()
