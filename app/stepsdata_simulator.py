import random
import datetime
import json
import os
from app import app, db  # Import app directly from your __init__.py
from app.models import User  # Import User model


# Function to generate random steps based on the day of the week
def generate_random_steps(start_date, end_date):
    step_data = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() >= 5:  # Saturday (5) or Sunday (6)
            steps = random.randint(8000, 13000)  # More steps on weekends
        else:
            steps = random.randint(4000, 10000)  # Fewer steps on weekdays

        step_data.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "steps": steps
        })
        current_date += datetime.timedelta(days=1)

    return step_data


# Ensure the static folder exists
static_folder = 'static'
if not os.path.exists(static_folder):
    os.makedirs(static_folder)

# File path to store step data
file_name = "all_users_step_data.json"
file_path = os.path.join(static_folder, file_name)

# Get yesterday's date
yesterday = datetime.date.today() - datetime.timedelta(days=1)

# Start and End date for the steps data (from 1st April to yesterday)
start_date = datetime.date(2025, 4, 1)

# Use the application context to query the database
with app.app_context():
    # Query the database to get all users
    users = User.query.all()

    # Dictionary to store steps data for each user
    user_steps_data = {}

    # Check if the file exists and load the existing data if present
    if os.path.exists(file_path):
        with open(file_path, 'r') as json_file:
            existing_data = json.load(json_file)
    else:
        existing_data = {}

    # Generate steps data for each user
    for user in users:
        # Get the username and existing steps data for that user
        existing_steps = existing_data.get(user.username, [])

        # If there is no existing data or the latest date is before yesterday, generate new data
        if existing_steps:
            last_date = datetime.datetime.strptime(existing_steps[-1]["date"], "%Y-%m-%d").date()
        else:
            last_date = start_date  # If no data exists, start from the defined start_date

        # Generate steps from the next day after the latest date
        if last_date < yesterday:
            new_steps = generate_random_steps(last_date + datetime.timedelta(days=1), yesterday)
            existing_steps.extend(new_steps)

        # Update the user's steps data in the dictionary
        user_steps_data[user.username] = existing_steps

    # Write or append the JSON data to the file
    with open(file_path, 'w') as json_file:
        json.dump(user_steps_data, json_file, indent=4)

    print(f"Saved/Updated step data for all users in {file_path}")
