import datetime
import random
from typing import List

from app import db, logger
from app.iot_simulator import generate_reading
from app.models import ActivityLog, User, Inventory, EnergyReading
from app.utils import load_buildings_data


# === Reset and Seed Database ===
def reset_db():
    """
    Drop all tables and recreate them with mock data:
    - Verified demo users
    - Activity logs
    - Inventory items
    - Energy readings
    """
    db.drop_all()
    db.create_all()

    # Seed mock users
    users = [
        {'email': 'tom.b12345@yopmail.com', 'role': 'Normal', 'pw': 'amy.pw'},
        {'email': 'yin.b12345@yopmail.com', 'role': 'Vendor', 'pw': 'amy.pw'},
        {'email': 'jo.b12345@yopmail.com', 'role': 'Normal', 'pw': 'amy.pw'}
    ]

    for u in users:
        pw = u.pop('pw')
        role = u.pop('role', 'Normal')
        user = User(**u)
        user.set_password(pw)
        user.email_verified = True
        user.role = role
        db.session.add(user)
    db.session.commit()
    logger.info("Mock user data generated successfully.")

    # Generate energy readings
    generate_sensor_data()
    db.session.commit()  # Commit users before adding dependent data

    # Generate inventory data
    create_mock_inventory_data()

    # Generate activity logs for each user
    for user in users:
        user_email = user['email']
        habit_factor = random.uniform(0.3, 0.6)
        logs = create_mock_activity_data(user_email, habit_factor)
        db.session.add_all(logs)

    db.session.commit()
    logger.info("Mock activity data generated for users successfully.")

# === Helper Functions ===

def generate_walking_data(date: datetime.date):
    """
    Generate mock walking data based on date (weekend vs weekday).
    """
    is_weekend = date.weekday() >= 5
    steps = random.randint(7000, 13000) if is_weekend else random.randint(4000, 10000)
    distance_km = round(steps * 0.0008, 2)
    eco_points = round(steps * 0.001, 2)
    return steps, distance_km, eco_points

def generate_cycling_data(date: datetime.date, intensity: float = 1.0):
    """
    Generate mock cycling data with intensity variations.
    """
    base = random.uniform(5.0, 12.0)
    variation = random.uniform(-2.0, 3.0)
    distance_km = round(max(0.0, base + variation) * intensity, 2)
    eco_points = round(distance_km * 0.5, 2)
    return distance_km, eco_points

def create_mock_activity_data(user_email: str, habit_factor: float = 0.4) -> List[ActivityLog]:
    """
    Generate realistic daily walking and semi-random cycling logs
    for the given user from April 1 to yesterday i.e. (T-1 Day).
    """
    tz_today = datetime.date.today()
    start_date = datetime.date(2025, 4, 1)
    yesterday = tz_today - datetime.timedelta(days=1)

    data = []
    current_date = start_date
    consecutive_no_cycling = 0

    while current_date <= yesterday:
        activity_date = datetime.datetime.combine(current_date, datetime.time.min)

        # --- Walking data (logged daily) ---
        walk_steps, walk_distance, walk_points = generate_walking_data(current_date)
        data.append(ActivityLog(
            email=user_email,
            date=activity_date,
            activity_type="walking",
            steps=walk_steps,
            distance=walk_distance,
            eco_points=walk_points,
            eco_last_updated=datetime.datetime.now(datetime.timezone.utc),
            eco_last_redeemed=None
        ))

        # --- Cycling data (logged probabilistically) ---
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

def create_mock_inventory_data():
    """
    Generate and seed random inventory items for all users.
    """
    categories = {
        "4 Cheese Pizza": "r",
        "Milk": "d",
        "Sour Dough Bread": "b",
        "Brioche Bread": "b",
        "Grape": "f",
        "Orange": "f",
        "Tomato": "f",
        "Churros": "b",
        "Gulab Jamun": "s",
        "Green Salad": "r",
        "Chicken Drumsticks": "m"
    }

    expiry_date = datetime.date.today() + datetime.timedelta(days=random.choice([0, 1, 2, 3]))
    users = User.query.all()

    for user in users:
        for _ in range(random.randint(5, 10)):  # 5–10 items per user
            name = random.choice(list(categories.keys()))
            product = Inventory(
                name=name,
                expiry_date=expiry_date,
                units=random.randint(1, 50),
                category=categories[name],
                marked_price=round(random.uniform(0.0, 20.0), 2),
                discount=round(random.uniform(0.1, 0.5), 2),
                final_price=0.0,  # To be calculated
                location=random.choice(["Nisa Local", "Spar", "Campus Living"]),
                user_id=user.id
            )
            product.final_price = round(product.marked_price * (1 - product.discount), 2)
            db.session.add(product)

    db.session.commit()
    logger.info("Mock inventory data generated successfully.")

def generate_sensor_data():
    """
    Generate mock energy readings every 5 minutes for the past 7 days
    for university buildings (and optionally accommodation flats).
    """
    university_buildings, accommodation_buildings = load_buildings_data()

    energy_types = ["electricity", "gas"]
    start_time = datetime.datetime.now() - datetime.timedelta(days=7)
    end_time = datetime.datetime.now()
    interval = datetime.timedelta(minutes=5)

    current_time = start_time
    batch = []

    while current_time <= end_time:
        # Readings for university buildings
        for building in university_buildings:
            for energy_type in energy_types:
                reading = EnergyReading(
                    timestamp=current_time,
                    building=building.get("building"),
                    building_code=building.get("building_code", ""),
                    zone=building.get("zone", ""),
                    value=generate_reading(energy_type),
                    category=energy_type
                )
                batch.append(reading)

        # Uncomment to simulate per-flat data for accommodations
        # for building in accommodation_buildings:
        #     total_flats = building.get("total_flats", 0)
        #     for flat_number in range(1, total_flats + 1):
        #         flat_building_name = f"{building['building']} Flat {flat_number}"
        #         for energy_type in energy_types:
        #             reading = EnergyReading(
        #                 timestamp=current_time,
        #                 building=flat_building_name,
        #                 building_code=building.get("building_code", ""),
        #                 zone=building.get("zone", ""),
        #                 value=generate_reading(energy_type),
        #                 category=energy_type
        #             )
        #             batch.append(reading)

        current_time += interval

        # Commit in batches to improve performance
        if len(batch) >= 1000:
            db.session.add_all(batch)
            db.session.commit()
            batch.clear()

    # Final commit for remaining data
    if batch:
        db.session.add_all(batch)
        db.session.commit()

    logger.info("Mock energy readings generated successfully.")
