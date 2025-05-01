import json
import os
from datetime import datetime, timedelta
from urllib.parse import urlsplit

import sqlalchemy as sa
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import func

from app import app
from app import db
from app.forms import LoginForm
from app.models import User, EnergyReading


@app.route("/")
def home():
    return render_template('home.html', title="Home")


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title="Account")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('generic_form.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
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
                           total_usage_by_zones=total_usage_by_zones)

basedir = os.path.abspath(os.path.dirname(__file__))

# Get distinct building names from the database
def get_building_names():
    buildings = db.session.query(EnergyReading.building).filter(EnergyReading.building_code != "").distinct().all()
    return [building[0] for building in buildings if building[0]]  # Filter out nulls if needed

@app.route('/get_energy_data', methods=['POST'])
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

# Error handlers
# See: https://en.wikipedia.org/wiki/List_of_HTTP_status_codes

# Error handler for 403 Forbidden
@app.errorhandler(403)
def error_403(error):
    return render_template('errors/403.html', title='Error'), 403

# Handler for 404 Not Found
@app.errorhandler(404)
def error_404(error):
    return render_template('errors/404.html', title='Error'), 404

@app.errorhandler(413)
def error_413(error):
    return render_template('errors/413.html', title='Error'), 413

# 500 Internal Server Error
@app.errorhandler(500)
def error_500(error):
    return render_template('errors/500.html', title='Error'), 500