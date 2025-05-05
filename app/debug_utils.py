import datetime
import random
from typing import List

from app import db
from app.models import ActivityLog, User


def reset_db():
    """Drop all tables and seed verified demo users with realistic activity logs."""
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
        u.pop('role', None)
        user = User(**u)
        user.set_password(pw)
        user.email_verified = True
        db.session.add(user)
    db.session.commit()

    tz_today = datetime.date.today()
    start_date = datetime.date(2025, 4, 1)
    yesterday = tz_today - datetime.timedelta(days=1)

    def generate_walking_data(date: datetime.date):
        is_weekend = date.weekday() >= 5
        steps = random.randint(7000, 13000) if is_weekend else random.randint(4000, 10000)
        distance_km = round(steps * 0.0008, 2)
        eco_points = round(steps * 0.001, 2)
        return steps, distance_km, eco_points

    def generate_cycling_data(date: datetime.date, intensity: float = 1.0):
        base = random.uniform(5.0, 12.0)
        variation = random.uniform(-2.0, 3.0)
        distance_km = round(max(0.0, base + variation) * intensity, 2)
        eco_points = round(distance_km * 0.5, 2)
        return distance_km, eco_points

    def create_mock_activity_data(user_email: str, habit_factor: float = 0.4) -> List[ActivityLog]:
        data = []
        current_date = start_date
        consecutive_no_cycling = 0

        while current_date <= yesterday:
            activity_date = datetime.datetime.combine(current_date, datetime.time.min)

            # Walking: daily
            walk_steps, walk_distance, walk_points = generate_walking_data(current_date)
            data.append(ActivityLog(
                email=user_email,
                date=activity_date,
                activity_type="walking",
                steps=walk_steps,
                distance=walk_distance,
                eco_points=walk_points,
                eco_last_updated=datetime.datetime.utcnow(),
                eco_last_redeemed=None
            ))

            # Cycling: 30–70% chance, avoids long dry spells
            day_offset = (current_date - start_date).days
            cycling_probability = min(habit_factor + 0.01 * (day_offset // 7), 0.7)
            should_cycle = random.random() < cycling_probability or consecutive_no_cycling >= 2

            if should_cycle:
                intensity = random.choice([0.8, 1.0, 1.2])
                cycle_distance, cycle_points = generate_cycling_data(current_date, intensity)
                if cycle_distance > 1.0:
                    consecutive_no_cycling = 0
                    data.append(ActivityLog(
                        email=user_email,
                        date=activity_date,
                        activity_type="cycling",
                        steps=0,
                        distance=cycle_distance,
                        eco_points=cycle_points,
                        eco_last_updated=datetime.datetime.utcnow(),
                        eco_last_redeemed=None
                    ))
                else:
                    consecutive_no_cycling += 1
            else:
                consecutive_no_cycling += 1

            current_date += datetime.timedelta(days=1)

        return data

    for user in users:
        user_email = user['email']
        habit_factor = random.uniform(0.3, 0.6)
        logs = create_mock_activity_data(user_email, habit_factor)
        db.session.add_all(logs)
    db.session.commit()
