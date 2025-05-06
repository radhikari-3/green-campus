from unittest.mock import patch

from app.views.food_expiry import calculate_user_eco_points


@patch('app.views.food_expiry.db.session.query')
def test_calculate_user_eco_points_valid_user(mock_query, fake_user):
    """
    Positive test case: Ensure eco points are calculated correctly for a valid user.
    """
    # Mock the database query to return a sum of eco points
    mock_query.return_value.filter.return_value.scalar.return_value = 100  # User has 100 eco points

    total_points, pounds = calculate_user_eco_points(fake_user.email)
    assert total_points == 100
    assert pounds == 2.0  # 100 points * 0.02 = £2.0


@patch('app.views.food_expiry.db.session.query')
def test_calculate_user_eco_points_no_points(mock_query, fake_user):
    """
    Negative test case: Ensure eco points calculation works when user has no points.
    """
    # Mock the database query to return None (no points)
    mock_query.return_value.filter.return_value.scalar.return_value = None

    total_points, pounds = calculate_user_eco_points(fake_user.email)
    assert total_points == 0  # No points
    assert pounds == 0.0  # No pounds

