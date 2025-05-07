from app import db
from app.models import User

# === Test: Basic App Configuration ===
def test_app_config(app):
    """
    Verifies that the Flask app is properly configured for testing.

    Assertions:
    - TESTING mode is enabled.
    - The app uses an in-memory SQLite database.
    - CSRF protection is disabled for tests.
    """
    assert app.config['TESTING'] is True
    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'
    assert app.config['WTF_CSRF_ENABLED'] is False


# === Test: In-Memory Database Functionality ===
def test_database_connection(app):
    """
    Confirms that the in-memory database works and can store/query data.

    Steps:
    1. Creates all tables.
    2. Inserts a test user into the database.
    3. Fetches the user and validates their email field.
    """
    with app.app_context():
        db.create_all()

        # Step 1: Insert a test user
        user = User(email="testdb@example.com", email_verified=True)
        user.set_password("testpass")
        db.session.add(user)
        db.session.commit()

        # Step 2: Query the user from the DB
        queried_user = db.session.query(User).filter_by(email="testdb@example.com").first()

        # Step 3: Assertions
        assert queried_user is not None
        assert queried_user.email == "testdb@example.com"
