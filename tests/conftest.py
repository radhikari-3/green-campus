import pytest
from app import create_app, db
from app.models import User

@pytest.fixture
def app():
    test_config = {
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    }

    app = create_app(test_config=test_config)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def fake_user():
    user = User(email="test@example.com", email_verified=True)
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user