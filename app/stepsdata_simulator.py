import random
import datetime
import json
import os


static_folder = 'static'
file_name     = "all_users_step_data.json"
file_path     = os.path.join(static_folder, file_name)


tz_today      = datetime.date.today()
start_date    = datetime.date(2025, 4, 1)
yesterday     = tz_today - datetime.timedelta(days=1)


if not os.path.exists(static_folder):
    os.makedirs(static_folder)



def generate_random_steps(start_date, end_date):

    step_data    = []
    current_date = start_date
    while current_date <= end_date:

        if current_date.weekday() >= 5:
            steps = random.randint(8_000, 13_000)
        else:
            steps = random.randint(4_000, 10_000)

        step_data.append({
            "date":  current_date.strftime("%Y-%m-%d"),
            "steps": steps
        })
        current_date += datetime.timedelta(days=1)

    return step_data



def run_steps_simulator():

    from app import app, db
    from app.models import User, StepData, EcoPoints

    with app.app_context():

        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                all_data = json.load(f)
        else:
            all_data = {}


        users = User.query.all()
        for u in users:
            history = all_data.get(u.username, [])
            if history:
                last = datetime.datetime.strptime(history[-1]["date"], "%Y-%m-%d").date()
            else:
                last = start_date - datetime.timedelta(days=1)

            if last < yesterday:
                new_batch = generate_random_steps(last + datetime.timedelta(days=1), yesterday)
                history.extend(new_batch)

            all_data[u.username] = history


        with open(file_path, 'w') as f:
            json.dump(all_data, f, indent=4)



        inserted_steps = 0
        for username, entries in all_data.items():
            for e in entries:
                entry_date = datetime.datetime.strptime(e["date"], "%Y-%m-%d").date()
                exists = StepData.query.filter_by(username=username, date=entry_date).first()
                if not exists:
                    sd = StepData(
                        username=username,
                        date=entry_date,
                        steps=e["steps"]
                    )
                    db.session.add(sd)
                    inserted_steps += 1
        db.session.commit()



        updated = 0
        for u in users:
            total_steps = db.session.query(
                db.func.sum(StepData.steps)
            ).filter_by(username=u.username).scalar() or 0

            eco_value = total_steps // 10_000
            now = datetime.datetime.utcnow()

            eco_entry = EcoPoints.query.filter_by(username=u.username).first()
            if eco_entry:
                eco_entry.eco_points = eco_value
                eco_entry.last_updated_at = now
            else:
                eco_entry = EcoPoints(
                    username=u.username,
                    eco_points=eco_value,
                    last_updated_at=now
                )
                db.session.add(eco_entry)
            updated += 1
        db.session.commit()


# optional standalone execution
# if __name__ == "__main__":
#     run_steps_simulator()
