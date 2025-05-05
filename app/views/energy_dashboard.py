import os
from datetime import datetime, timedelta

from flask import Blueprint, request, render_template, jsonify
from sqlalchemy import func

from app import db
from app.models import EnergyReading

energy_bp = Blueprint('energy_dash', __name__)


@energy_bp.route('/energy_analytics', methods=['GET'])
def energy_dashboard():
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

    print("zonal data", total_usage_by_zones)

    return render_template('energy_dashboard.html', buildings=buildings,
                           total_usage_by_zones=total_usage_by_zones, title="Energy Analytics")

basedir = os.path.abspath(os.path.dirname(__file__))

# Get distinct building names from the database
def get_building_names():
    buildings = db.session.query(EnergyReading.building).filter(EnergyReading.building_code != "").distinct().all()
    return [building[0] for building in buildings if building[0]]  # Filter out nulls if needed

@energy_bp.route('/get_energy_data', methods=['POST'])
def get_line_chart_view():
    data = request.get_json()
    buildings = data.get('buildings', [])
    energy_type = data.get('energy_type', 'both')
    time_range = data.get('time_range', 'daily')
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    traces = []

    # Handle date range
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        end_date = datetime.today()
        start_date = end_date - timedelta(days=30)

    for building in buildings:
        energy_types = ['electricity', 'gas'] if energy_type == 'both' else [energy_type]

        for etype in energy_types:
            readings = (
                db.session.query(EnergyReading)
                .filter(
                    EnergyReading.building == building,
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

    return jsonify({'traces': traces})

def get_energy_usage_by_zone():
    results = (
        db.session.query(
            EnergyReading.zone,
            EnergyReading.category,
            func.sum(EnergyReading.value).label('total_usage')
        )
        .filter(
            EnergyReading.building_code != ""
        )
        .group_by(EnergyReading.zone, EnergyReading.category)
        .all()
    )

    # Split results into electricity and gas usage
    electricity_usage = {}
    gas_usage = {}

    for zone, category, total in results:
        if category.lower() == 'electricity':
            electricity_usage[zone] = total
        elif category.lower() == 'gas':
            gas_usage[zone] = total

    return electricity_usage, gas_usage