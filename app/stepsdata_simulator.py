import random
import datetime
from app import app, db
from app.models import User, ActivityLog

tz_today   = datetime.date.today()
start_date = datetime.date(2025, 4, 1)
yesterday  = tz_today - datetime.timedelta(days=1)

def generate_random_step_count(date):
    if date.weekday() >= 5:
        return random.randint(8000, 13000)
    else:
        return random.randint(4000, 10000)

def generate_random_cycle_distance():
    return round(random.uniform(3.5, 20.0), 2)  # Updated range

def run_steps_simulator():
    with app.app_context():
        users = User.query.all()

        for user in users:
            latest_entry = db.session.query(
                db.func.max(ActivityLog.date)
            ).filter_by(email=user.email).scalar()

            if latest_entry:
                last_date = latest_entry.date()
            else:
                last_date = start_date - datetime.timedelta(days=1)

            current = last_date + datetime.timedelta(days=1)

            while current <= yesterday:
                now = datetime.datetime.utcnow()

                # WALKING
                steps = generate_random_step_count(current)
                distance = round(steps / 1450, 2)
                eco_points = round(steps / 10000, 2)  # ✅ float division

                db.session.add(ActivityLog(
                    email=user.email,
                    date=datetime.datetime.combine(current, datetime.time()),
                    activity_type="walking",
                    steps=steps,
                    distance=distance,
                    eco_points=eco_points,
                    eco_last_updated=now
                ))

                # CYCLING
                if random.random() < 0.5:
                    cycle_distance = generate_random_cycle_distance()
                    cycle_eco_points = round(cycle_distance / 5, 2)  # ✅ float division

                    db.session.add(ActivityLog(
                        email=user.email,
                        date=datetime.datetime.combine(current, datetime.time()),
                        activity_type="cycling",
                        steps=0,
                        distance=cycle_distance,
                        eco_points=cycle_eco_points,
                        eco_last_updated=now
                    ))

                current += datetime.timedelta(days=1)

        db.session.commit()
