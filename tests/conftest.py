print("Loading conftest.py")
import pytest
from app import create_app, db
from app.models import User

@pytest.fixture(scope="module")
def app():
    """
    Create a Flask app instance for testing with an in-memory SQLite database.
    """
    test_config = {
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # In-memory database
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,  # Suppress warnings
        'SQLALCHEMY_ECHO': False,  # Disable SQL logging for cleaner test output
    }
    #print("Test config URI:", test_config['SQLALCHEMY_DATABASE_URI'])  # Debug point 1
    app = create_app(config_class=None, test_config=test_config)
    #print("App config after creation:", app.config.get('SQLALCHEMY_DATABASE_URI'))  # Debug point 2

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['DATABASE_URL'] = None
    app.config['SERVER_NAME'] = 'localhost'
    app.config['APPLICATION_ROOT'] = '/'
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    #print("Forced SQLite URI:", app.config.get('SQLALCHEMY_DATABASE_URI'))  # Debug point 3

    with app.app_context():
        db.create_all()  # Create tables
        yield app  # Yield app for use in tests
        db.session.remove()  # Clean up session
        db.drop_all()  # Drop tables after tests

@pytest.fixture
def client(app):
    """
    Provide a test client for the Flask app.
    """
    #print("Client config URI:", app.config.get('SQLALCHEMY_DATABASE_URI'))  # Debug point 4
    return app.test_client()

@pytest.fixture
def fake_user(app):
    """
    Create a fake user in the database for testing.
    """
    with app.app_context():
        user = User(email="test@example.com", email_verified=True)
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        yield user
        # Clean up user after test
        db.session.delete(user)
        db.session.commit()

@pytest.fixture
def logged_in_client(app, fake_user):
    """
    Provide a test client logged in as the fake user.
    """
    client = app.test_client()
    with app.app_context():
        with client.session_transaction() as sess:
            sess['user_id'] = fake_user.id  # Example session setup
        yield client

@pytest.fixture
def db_session(app):
    with app.app_context():
        yield db.session