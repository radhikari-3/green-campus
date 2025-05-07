from datetime import datetime
from unittest.mock import MagicMock

print("Loading conftest.py")

import pytest
from app import create_app, db
from app.models import User

# === Fixture: Create Test App ===
@pytest.fixture(scope="module")
def app():
    """
    Create and configure a Flask app instance for testing using an in-memory SQLite database.
    This app will be shared across all tests in the module.
    """
    test_config = {
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for form testing
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # Use in-memory DB for fast test setup
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SQLALCHEMY_ECHO': False,
        'SERVER_NAME': 'localhost',
        'APPLICATION_ROOT': '/',
        'PREFERRED_URL_SCHEME': 'http'
    }

    app = create_app(config_class=None, test_config=test_config)

    with app.app_context():
        db.create_all()  # Create all tables for testing
        yield app        # Provide the app to tests
        db.session.remove()
        db.drop_all()    # Clean up DB schema after tests finish


# === Fixture: Flask Test Client ===
@pytest.fixture
def client(app):
    """
    Return a test client for the Flask app. Used to simulate HTTP requests.
    """
    return app.test_client()


# === Fixture: Create a Fake Verified User ===
@pytest.fixture
def fake_user(app):
    """
    Add a test user to the database for login-based tests.
    Yields the user object and deletes it after the test ends.
    """
    with app.app_context():
        user = User(email="test@example.com", email_verified=True)
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        yield user
        # Cleanup: remove test user from DB
        db.session.delete(user)
        db.session.commit()


# === Fixture: Database Session with Rollback ===
@pytest.fixture(scope="function")
def db_session(app):
    """
    Provides an isolated database session per test.
    Rolls back any changes after each test to ensure clean state.
    """
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        options = dict(bind=connection, binds={})
        session = db.session
        yield session
        transaction.rollback()  # Undo all changes made during test
        connection.close()
        session.remove()


# === Fixture: Mocked EnergyReading Records ===
@pytest.fixture
def mock_energy_readings():
    """
    Provides a list of mocked energy readings for testing without querying the DB.
    Useful for analytics and chart generation tests.
    """
    return [
        MagicMock(building="Building A", category="electricity", value=100, timestamp=datetime(2023, 10, 1, 12, 0)),
        MagicMock(building="Building A", category="electricity", value=200, timestamp=datetime(2023, 10, 2, 12, 0)),
        MagicMock(building="Building B", category="gas", value=300, timestamp=datetime(2023, 10, 1, 12, 0)),
    ]
