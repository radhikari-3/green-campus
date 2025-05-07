from unittest.mock import patch
from flask import url_for

from app.views.energy_analytics import get_building_names, get_energy_usage_by_zone


# === Unit Test: get_building_names ===
@patch('app.views.energy_analytics.db.session.query')
def test_get_building_names(mock_query, db_session):
    """
     Scenario: Mock database query to fetch building names.
     Expected: Should return a list of building names.
    """
    mock_query.return_value.filter.return_value.distinct.return_value.all.return_value = [
        ('Building A',), ('Building B',), ('Building C',)
    ]

    buildings = get_building_names()
    assert buildings == ['Building A', 'Building B', 'Building C']


# === Unit Test: get_energy_usage_by_zone ===
@patch('app.views.energy_analytics.db.session.query')
def test_get_energy_usage_by_zone(mock_query, db_session):
    """
     Scenario: Mock database to return grouped energy usage.
     Expected: Should categorize data into electricity and gas.
    """
    mock_query.return_value.filter.return_value.group_by.return_value.all.return_value = [
        ('Zone 1', 'electricity', 1000),
        ('Zone 1', 'gas', 500),
        ('Zone 2', 'electricity', 1500),
    ]

    electricity_usage, gas_usage = get_energy_usage_by_zone()
    assert electricity_usage == {'Zone 1': 1000, 'Zone 2': 1500}
    assert gas_usage == {'Zone 1': 500}


# === Integration Test: Dashboard View ===
def test_energy_dashboard_view(db_session, client):
    """
     Scenario: Access the /energy_analytics dashboard route.
     Expected: Should return HTTP 200 and render expected content.
    """
    response = client.get(url_for('energy_dash.energy_dashboard'))
    assert response.status_code == 200
    assert b"Energy Analytics" in response.data


# === Unit Test: Empty Building Query ===
@patch('app.views.energy_analytics.db.session.query')
def test_get_building_names_empty(mock_query, db_session):
    """
     Scenario: No buildings found in the database.
     Expected: Return an empty list.
    """
    mock_query.return_value.filter.return_value.distinct.return_value.all.return_value = []
    buildings = get_building_names()
    assert buildings == []


# === Unit Test: Empty Energy Usage Query ===
@patch('app.views.energy_analytics.db.session.query')
def test_get_energy_usage_by_zone_empty(mock_query, db_session):
    """
     Scenario: No usage data returned.
     Expected: Return empty dictionaries for both electricity and gas.
    """
    mock_query.return_value.filter.return_value.group_by.return_value.all.return_value = []
    electricity_usage, gas_usage = get_energy_usage_by_zone()
    assert electricity_usage == {}
    assert gas_usage == {}


# === Negative Test: Invalid Line Chart Payload ===
def test_get_line_chart_view_invalid_payload(db_session, client):
    """
     Scenario: POST with incomplete JSON body (missing required keys).
     Expected: Return empty 'traces' list in response.
    """
    response = client.post(
        url_for('energy_dash.get_line_chart_view'),
        json={'buildings': ['Building A']}  # Missing required fields
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['traces'] == []


# === Unit Test: Handle Invalid Data in Energy Usage ===
@patch('app.views.energy_analytics.db.session.query')
def test_get_energy_usage_by_zone_invalid_data(mock_query, db_session):
    """
    ️ Scenario: DB returns invalid or unexpected usage data.
     Expected: Gracefully handle None values and unknown categories.
    """
    mock_query.return_value.filter.return_value.group_by.return_value.all.return_value = [
        ('Zone 1', 'electricity', None),    # Invalid total usage
        ('Zone 2', 'unknown', 500),         # Unknown category
    ]

    electricity_usage, gas_usage = get_energy_usage_by_zone()
    assert electricity_usage == {'Zone 1': 0}  # Default to 0 for None
    assert gas_usage == {}  # Skip unknown categories
