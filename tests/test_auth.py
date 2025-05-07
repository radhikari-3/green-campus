from flask import url_for
from app.models import User

# === Test: Login Attempt with Unverified Email ===
def test_login_with_unverified_email(client, db_session):
    """
    Test Case:
    - Scenario: A user tries to log in with valid credentials but has not verified their email.
    - Expected Behavior: The application should prevent login and show a warning message.

    Steps:
    1. Create a user with an unverified email.
    2. Submit a POST request to the login endpoint.
    3. Assert that the response contains the warning message about email verification.
    """
    # Step 1: Create a test user without verifying the email
    user = User(email='unverified@example.com')
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()

    # Step 2: Attempt to log in with the unverified account
    response = client.post(url_for('auth.login'), data={
        'email': 'unverified@example.com',
        'password': 'password123'
    }, follow_redirects=True)

    # Step 3: Verify the login is blocked with the appropriate message
    assert b'Please verify your email before logging in' in response.data
