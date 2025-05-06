# test_basic.py
from app import db
from app.models import User


def test_app_config(app):
    """
    Test that the app is configured for testing with SQLite.
    """
    assert app.config['TESTING'] is True
    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'
    assert app.config['WTF_CSRF_ENABLED'] is False


def test_database_connection(app):
    """
    Test that the in-memory SQLite database is accessible.
    """
    with app.app_context():
        # Create a test table and insert data
        db.create_all()
        user = User(email="testdb@example.com", email_verified=True)
        user.set_password("testpass")
        db.session.add(user)
        db.session.commit()

        # Query the database
        queried_user = db.session.query(User).filter_by(email="testdb@example.com").first()
        assert queried_user is not None
        assert queried_user.email == "testdb@example.com"
