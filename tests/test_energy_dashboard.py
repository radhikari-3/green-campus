from unittest.mock import patch

from flask import url_for

from app.views.energy_analytics import get_building_names, get_energy_usage_by_zone


# Scenario: Mock database query to fetch building names.
    # Expected: Return a list of building names.




@patch('app.views.energy_analytics.db.session.query')
def test_get_building_names(mock_query, db_session):
    # Scenario: Mock database query to fetch building names.
    # Expected: Return a list of building names.
    mock_query.return_value.filter.return_value.distinct.return_value.all.return_value = [
        ('Building A',), ('Building B',), ('Building C',)
    ]

    buildings = get_building_names()
    assert buildings == ['Building A', 'Building B', 'Building C']


@patch('app.views.energy_analytics.db.session.query')
def test_get_energy_usage_by_zone(mock_query, db_session):
    # Scenario: Mock database query to fetch energy usage by zone.
    # Expected: Return energy usage data grouped by zone and category.
    mock_query.return_value.filter.return_value.group_by.return_value.all.return_value = [
        ('Zone 1', 'electricity', 1000),
        ('Zone 1', 'gas', 500),
        ('Zone 2', 'electricity', 1500),
    ]

    electricity_usage, gas_usage = get_energy_usage_by_zone()
    assert electricity_usage == {'Zone 1': 1000, 'Zone 2': 1500}
    assert gas_usage == {'Zone 1': 500}


def test_energy_dashboard_view(db_session, client):
    # Scenario: Verify the energy dashboard page loads successfully.
    # Expected: Page should return a 200 status code and display relevant content.
    response = client.get(url_for('energy_dash.energy_dashboard'))
    assert response.status_code == 200
    assert b"Energy Analytics" in response.data


@patch('app.views.energy_analytics.db.session.query')
def test_get_building_names_empty(mock_query, db_session):
    # Mock database query to return no buildings
    mock_query.return_value.filter.return_value.distinct.return_value.all.return_value = []

    buildings = get_building_names()
    assert buildings == []  # Expect an empty list


@patch('app.views.energy_analytics.db.session.query')
def test_get_energy_usage_by_zone_empty(mock_query, db_session):
    # Mock database query to return no energy usage data
    mock_query.return_value.filter.return_value.group_by.return_value.all.return_value = []

    electricity_usage, gas_usage = get_energy_usage_by_zone()
    assert electricity_usage == {}  # Expect an empty dictionary
    assert gas_usage == {}  # Expect an empty dictionary



def test_get_line_chart_view_invalid_payload(db_session, client):
    # Send an invalid payload (missing required fields)
    response = client.post(
        url_for('energy_dash.get_line_chart_view'),
        json={
            'buildings': ['Building A']
            # Missing 'energy_type', 'time_range', 'start_date', 'end_date'
        }
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['traces'] == []  # Expect no traces due to incomplete payload


@patch('app.views.energy_analytics.db.session.query')
def test_get_energy_usage_by_zone_invalid_data(mock_query, db_session):
    # Scenario: Handle invalid energy usage data gracefully.
    # Expected: Return default values for invalid or missing data.
    mock_query.return_value.filter.return_value.group_by.return_value.all.return_value = [
        ('Zone 1', 'electricity', None),  # Invalid total usage (None)
        ('Zone 2', 'unknown', 500),  # Invalid category
    ]

    electricity_usage, gas_usage = get_energy_usage_by_zone()
    assert electricity_usage == {'Zone 1': 0}  # Expect 0 for invalid total usage
    assert gas_usage == {}  # Ignore invalid category
