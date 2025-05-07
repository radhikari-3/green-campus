from unittest.mock import patch
from app.views.food_expiry import calculate_user_eco_points

# === Unit Test: Valid User with 100 Eco Points ===
@patch('app.views.food_expiry.db.session.query')
def test_calculate_user_eco_points_valid_user(mock_query, fake_user):
    """
    Positive test case:
    Scenario: A verified user has 100 eco points in the database.
    Expected:
    - Total eco points should be 100.
    - Monetary equivalent should be £2.00.
    """
    mock_query.return_value.filter.return_value.scalar.return_value = 100  # Simulate DB result

    total_points, pounds = calculate_user_eco_points(fake_user.email)
    assert total_points == 100
    assert pounds == 2.0  # 100 * 0.02


# === Unit Test: Valid User with 5 Eco Points (Negative Assertion) ===
@patch('app.views.food_expiry.db.session.query')
def test_calculate_user_eco_points_valid_user_negative(mock_query, fake_user):
    """
    Semi-negative test case:
    Scenario: A verified user has 5 eco points.
    Expected:
    - Ensure the system does not mistakenly report 10 points or £2.00.
    """
    mock_query.return_value.filter.return_value.scalar.return_value = 5

    total_points, pounds = calculate_user_eco_points(fake_user.email)
    assert total_points != 10
    assert pounds != 2.0


# === Unit Test: User with No Activity Logs ===
@patch('app.views.food_expiry.db.session.query')
def test_calculate_user_eco_points_no_points(mock_query, fake_user):
    """
    Negative test case:
    Scenario: A user has no activity logs (DB returns None).
    Expected:
    - Total eco points should default to 0.
    - Monetary equivalent should be £0.00.
    """
    mock_query.return_value.filter.return_value.scalar.return_value = None

    total_points, pounds = calculate_user_eco_points(fake_user.email)
    assert total_points == 0
    assert pounds == 0.0
