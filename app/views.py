from urllib.parse import urlsplit

import sqlalchemy as sa
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
import os
import json
from app import app
from app import db
from app.forms import LoginForm
from app.models import User


@app.route("/")
def home():
    return render_template('home.html', title="Home")


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title="Account")

@app.route("/eco-points-dashboard")
@login_required
def eco_points_dashboard():
    try:
        with open(os.path.join("app", "static", "all_users_step_data.json")) as f:
            all_data = json.load(f)
    except FileNotFoundError:
        all_data = {}

    username = current_user.username
    user_data = all_data.get(username, [])

    # Calculate average steps across all users by date
    date_to_steps = {}
    for user_steps in all_data.values():
        for entry in user_steps:
            date = entry["date"]
            date_to_steps.setdefault(date, []).append(entry["steps"])

    avg_data = [
        {"date": date, "steps": sum(steps) // len(steps)}
        for date, steps in sorted(date_to_steps.items())
    ]

    return render_template(
        "eco_points_dashboard.html",
        title="Eco Points Dashboard",
        username=username,
        user_data=user_data,
        avg_data=avg_data
    )




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