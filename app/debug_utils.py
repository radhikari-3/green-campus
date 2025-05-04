import datetime
import random
from typing import List

from app import db
from app.models import User, ActivityLog
from app.logger import logger as log
#from app.stepsdata_simulator import run_steps_simulator
from sqlalchemy import text

def reset_db():
    """ Drop all tables and seed verified demo users. """
    db.drop_all()
    db.create_all()

    users = [
        {'email': 'amy.b12345@yopmail.com', 'role': 'Admin', 'pw': 'amy.pw'},
        {'email': 'tom.b12345@yopmail.com', 'pw': 'amy.pw'},
        {'email': 'yin.b12345@yopmail.com', 'role': 'Admin', 'pw': 'amy.pw'},
        {'email': 'trq.b12345@yopmail.com', 'pw': 'amy.pw'},
        {'email': 'jo.b12345@yopmail.com', 'pw': 'amy.pw'}
    ]

    for u in users:
        pw = u.pop('pw')
        u.pop('role', None)  # Remove 'role' if present

        user = User(**u)
        user.set_password(pw)
        user.email_verified = True
        db.session.add(user)

    db.session.commit()

    tz_today = datetime.date.today()
    start_date = datetime.date(2025, 4, 1)
    yesterday = tz_today - datetime.timedelta(days=1)

    def generate_random_step_count(date):
        if date.weekday() >= 5:  # Saturday or Sunday
            return random.randint(8000, 13000)
        else:
            return random.randint(4000, 10000)

    def create_mock_activity_data(user_email: str) -> List[ActivityLog]:
        data = []
        current_date = start_date
        while current_date <= yesterday:
            # --- Walking: always happens ---
            walk_steps = generate_random_step_count(current_date)
            walk_distance = round(walk_steps * 0.0008, 2)
            walk_eco_points = round(walk_steps * 0.001, 2)

            walk_activity = ActivityLog(
                email=user_email,
                date=datetime.datetime.combine(current_date, datetime.time.min),
                activity_type="walking",
                steps=walk_steps,
                distance=walk_distance,
                eco_points=walk_eco_points,
                eco_last_updated=datetime.datetime.utcnow(),
                eco_last_redeemed=None
            )
            data.append(walk_activity)

            # --- Cycling: happens more on weekends, sometimes on weekdays ---
            cycle_today = False
            if current_date.weekday() >= 5:
                # Weekend → higher chance of cycling
                cycle_today = random.random() < 0.8
            else:
                # Weekday → lower chance of casual cycling
                cycle_today = random.random() < 0.2

            if cycle_today:
                cycle_distance = round(random.uniform(3.5, 20.0), 2)
                cycle_eco_points = round(cycle_distance * 0.5, 2)

                cycle_activity = ActivityLog(
                    email=user_email,
                    date=datetime.datetime.combine(current_date, datetime.time.min),
                    activity_type="cycling",
                    steps=0,
                    distance=cycle_distance,
                    eco_points=cycle_eco_points,
                    eco_last_updated=datetime.datetime.utcnow(),
                    eco_last_redeemed=None
                )
                data.append(cycle_activity)

            current_date += datetime.timedelta(days=1)

        return data

    for user in users:
        mock_data = create_mock_activity_data(user['email'])
        db.session.add_all(mock_data)
        db.session.commit()