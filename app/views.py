from urllib.parse import urlsplit


import sqlalchemy as sa
from sqlalchemy import func
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required

from app import app, db
from app.forms import LoginForm
from app.models import User, ActivityLog


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
    email = current_user.email


    walking_q = (
        ActivityLog.query
        .filter_by(email=email, activity_type="walking")
        .order_by(ActivityLog.date)
        .all()
    )
    walking_data = [
        {"date": al.date.strftime("%Y-%m-%d"), "steps": al.steps}
        for al in walking_q
    ]


    cycling_q = (
        ActivityLog.query
        .filter_by(email=email, activity_type="cycling")
        .order_by(ActivityLog.date)
        .all()
    )
    cycling_data = [
        {"date": al.date.strftime("%Y-%m-%d"), "distance": al.distance}
        for al in cycling_q
    ]


    avg_q = (
        db.session.query(
            func.date(ActivityLog.date).label("date"),
            func.avg(ActivityLog.steps).label("avg_steps")
        )
        .filter(ActivityLog.activity_type == "walking")
        .group_by(func.date(ActivityLog.date))
        .order_by(func.date(ActivityLog.date))
        .all()
    )
    avg_data = [
        {"date": row.date.strftime("%Y-%m-%d"), "steps": round(row.avg_steps)}
        for row in avg_q
    ]


    total_eco_points = (
        db.session.query(func.sum(ActivityLog.eco_points))
        .filter(ActivityLog.email == email)
        .scalar() or 0
    )

    return render_template(
        "eco_points_dashboard.html",
        title="Eco Points Dashboard",
        username=email,
        walking_data=walking_data,
        cycling_data=cycling_data,
        avg_data=avg_data,
        eco_points=round(total_eco_points, 2)
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )
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
@app.errorhandler(403)
def error_403(error):
    return render_template('errors/403.html', title='Error'), 403

@app.errorhandler(404)
def error_404(error):
    return render_template('errors/404.html', title='Error'), 404

@app.errorhandler(413)
def error_413(error):
    return render_template('errors/413.html', title='Error'), 413

@app.errorhandler(500)
def error_500(error):
    return render_template('errors/500.html', title='Error'), 500
