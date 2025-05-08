from datetime import datetime, timedelta

from flask import Blueprint, request, render_template, jsonify
from sqlalchemy import func

from app import db
from app.models import EnergyReading, Building

# === Blueprint Setup ===
energy_bp = Blueprint('energy_dash', __name__)


# === Route: Energy Analytics Dashboard (GET) ===
@energy_bp.route('/energy_analytics', methods=['GET'])
def energy_dashboard():
    """
    Renders the energy dashboard with electricity and gas usage aggregated by zone.
    """
    buildings = get_building_names()
    electricity_usage, gas_usage = get_energy_usage_by_zone()

    total_usage_by_zones = {
        'electricity_usage': {
            'labels': list(electricity_usage.keys()) if electricity_usage else [],
            'data': list(electricity_usage.values()) if electricity_usage else []
        },
        'gas_usage': {
            'labels': list(gas_usage.keys()) if gas_usage else [],
            'data': list(gas_usage.values()) if gas_usage else []
        }
    }

    return render_template('energy_dashboard.html',
                           buildings=buildings,
                           total_usage_by_zones=total_usage_by_zones,
                           title="Energy Analytics")


# === Route: Fetch Line Chart Data for Energy Usage (POST) ===
@energy_bp.route('/get_energy_data', methods=['POST'])
def get_line_chart_view():
    """
    Returns energy usage time-series traces for selected buildings and date range.
    """
    data = request.get_json()
    buildings = data.get('buildings', [])
    energy_type = data.get('energy_type', 'both')
    time_range = data.get('time_range', 'daily')  # Not currently used
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    traces = get_traces(buildings, energy_type, start_date, end_date)
    return jsonify({'traces': traces})


# === Route: Fetch Line Chart Data for CO2 Emissions (POST) ===
@energy_bp.route('/get_co2_energy_data', methods=['POST'])
def get_emissions_line_chart_view():
    """
    Returns CO₂ emission traces derived from energy usage data.
    """
    data = request.get_json()
    buildings = data.get('buildings', [])
    energy_type = data.get('energy_type', 'both')
    time_range = data.get('time_range', 'monthly')  # Not used
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    CO2_FACTORS = {
        'electricity': 0.233,  # kg CO₂ per kWh
        'gas': 0.184
    }

    traces = []

    # Parse date range
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        end_date = datetime.today()
        start_date = end_date - timedelta(days=30)

    # Loop through buildings and fetch daily total emissions
    for building in buildings:
        emissions_by_time = {}
        energy_types = ['electricity', 'gas'] if energy_type == 'both' else [energy_type]

        for etype in energy_types:
            building = get_building_id_by_name(building)
            readings = db.session.query(
                func.date(EnergyReading.timestamp).label('date'),
                func.sum(EnergyReading.value).label('value')
            ).join(Building, EnergyReading.building_id == Building.id).filter(
                Building.id == building,  # Use building.id to filter by building
                EnergyReading.category == etype,
                EnergyReading.timestamp >= start_date,
                EnergyReading.timestamp <= end_date
            ).group_by(
                func.date(EnergyReading.timestamp)
            ).order_by(
                func.date(EnergyReading.timestamp)
            ).all()

            for date, total_value in readings:
                date_str = date.strftime('%Y-%m-%d')
                emissions = total_value * CO2_FACTORS.get(etype, 0)
                emissions_by_time[date_str] = emissions_by_time.get(date_str, 0) + emissions

        traces.append({
            'x': list(emissions_by_time.keys()),
            'y': list(emissions_by_time.values()),
            'type': 'scatter',
            'mode': 'lines',
            'name': f"{building} - Total CO₂ Emissions"
        })

    return jsonify({'traces': traces})


# === Helper: Get Time-Series Energy Traces ===
def get_traces(buildings, energy_type, start_date, end_date):
    """
    Returns line chart data for energy usage per building.
    """
    
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        end_date = datetime.today()
        start_date = end_date - timedelta(days=30)

    traces = []
    
    for building in buildings:
        energy_types = ['electricity', 'gas'] if energy_type == 'both' else [energy_type]
        building = get_building_id_by_name(building)
        for etype in energy_types:
            readings = (
                db.session.query(EnergyReading)
                .join(Building,
                      EnergyReading.building_id == Building.id)  # Correctly join with Building table using building_id
                .filter(
                    Building.id == building,
                    # Use building.id for comparison, assuming 'building' is a Building instance
                    EnergyReading.category == etype,
                    EnergyReading.timestamp >= start_date,
                    EnergyReading.timestamp <= end_date
                )
                .order_by(EnergyReading.timestamp)
                .all()
            )

            if readings:
                x_vals = [r.timestamp.strftime('%Y-%m-%d %H:%M:%S') for r in readings]
                y_vals = [r.value for r in readings]

                traces.append({
                    'x': x_vals,
                    'y': y_vals,
                    'type': 'scatter',
                    'mode': 'lines',
                    'name': f"{building} - {etype.capitalize()}"
                })

    return traces


# === Helper: Get Aggregated Energy Usage by Zone ===
def get_energy_usage_by_zone():
    """
    Returns total electricity and gas usage grouped by zone.
    """
    building_ids = get_building_ids()

    results = (
        db.session.query(
            Building.zone,
            EnergyReading.category,
            func.sum(EnergyReading.value).label('total_usage')
        )
        .join(Building, EnergyReading.building_id == Building.id)
        .filter(Building.code != "", Building.id.in_(building_ids))
        .group_by(Building.zone, EnergyReading.category)
        .all()
    )

    electricity_usage = {}
    gas_usage = {}

    for zone, category, total in results:
        total = total or 0
        if category.lower() == 'electricity':
            electricity_usage[zone] = total
        elif category.lower() == 'gas':
            gas_usage[zone] = total

    return electricity_usage, gas_usage


# === Helper: Get Unique Building Names (non-empty codes only) ===
def get_building_names():
    """
    Returns a list of distinct building names from the EnergyReading table.
    """
    buildings = db.session.query(Building.name)\
        .filter(Building.code != "")\
        .distinct().all()

    return [building[0] for building in buildings if building[0]]

def get_building_ids():
    """
    Returns a list of distinct building IDs from the EnergyReading table.
    """
    buildings = db.session.query(Building.id)\
        .filter(Building.code != "")\
        .distinct().all()

    return [building[0] for building in buildings if building[0]]


def get_building_id_by_name(building_name):
    """
    Returns the building ID for a given building name.
    """
    building = db.session.query(Building.id) \
        .filter(Building.name == building_name) \
        .first()

    return building[0] if building else None
