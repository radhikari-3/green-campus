from flask import url_for
from sqlalchemy import select
from werkzeug.security import check_password_hash

from app.models import User


def test_login_with_unverified_email(client, db_session):
    user = User(email='unverified@example.com')
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    response = client.post(url_for('auth.login'), data={
        'email': 'unverified@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert b'Please verify your email before logging in' in response.data
