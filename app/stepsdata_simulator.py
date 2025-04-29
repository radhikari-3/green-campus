import random
import datetime
import json
import os

def generate_random_steps(start_date, end_date):
    step_data = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() >= 5:
            steps = random.randint(8000, 13000)
        else:
            steps = random.randint(4000, 10000)

        step_data.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "steps": steps
        })
        current_date += datetime.timedelta(days=1)

    return step_data

static_folder = 'static'
if not os.path.exists(static_folder):
    os.makedirs(static_folder)

file_name = "all_users_step_data.json"
file_path = os.path.join(static_folder, file_name)

yesterday = datetime.date.today() - datetime.timedelta(days=1)
start_date = datetime.date(2025, 4, 1)

def run_steps_simulator():
    from app import app, db
    from app.models import User

    with app.app_context():
        users = User.query.all()
        user_steps_data = {}

        if os.path.exists(file_path):
            with open(file_path, 'r') as json_file:
                existing_data = json.load(json_file)
        else:
            existing_data = {}

        for user in users:
            existing_steps = existing_data.get(user.username, [])

            if existing_steps:
                last_date = datetime.datetime.strptime(existing_steps[-1]["date"], "%Y-%m-%d").date()
            else:
                last_date = start_date

            if last_date < yesterday:
                new_steps = generate_random_steps(last_date + datetime.timedelta(days=1), yesterday)
                existing_steps.extend(new_steps)

            user_steps_data[user.username] = existing_steps

        with open(file_path, 'w') as json_file:
            json.dump(user_steps_data, json_file, indent=4)

        print(f"Saved/Updated step data for all users in {file_path}")
