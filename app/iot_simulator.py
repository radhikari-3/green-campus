import json
import os
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

from app import logger
from app.extensions import db
from app.models import EnergyReading

# === MQTT CONFIGURATION ===
BROKER = 'localhost'                    # MQTT broker address
PORT = 1883                             # Default MQTT port
TOPIC_ELECTRICITY = 'uob/electricity'  # Topic for electricity readings
TOPIC_GAS = 'uob/gas'                  # Topic for gas readings
PUBLISH_INTERVAL = 300                 # Publish every 5 minutes
BATCH_SIZE = 200                       # Commit readings to DB in batches of 200

# Temporary storage for sensor readings before batch commit
readings_to_add = []

# Path to current directory
basedir = os.path.abspath(os.path.dirname(__file__))


# === MQTT CONNECTION FUNCTION ===
def connect_mqtt():
    """Connects to the MQTT broker and returns the client object."""
    client = mqtt.Client()
    client.connect(BROKER, PORT)
    return client


# === SENSOR DATA SIMULATION ===
def generate_reading(sensor_type):
    """
    Simulate realistic energy readings for electricity or gas
    depending on time of day and weekday/weekend.
    """
    now = datetime.now()
    hour = now.hour
    weekday = now.weekday()

    if sensor_type == 'electricity':
        base = random.uniform(300, 600) if 8 <= hour < 18 else random.uniform(50, 200)
        if weekday >= 5:  # Weekend
            base *= 0.6
    elif sensor_type == 'gas':
        base = random.uniform(20, 50) if 8 <= hour < 18 else random.uniform(5, 20)
        if weekday >= 5:
            base *= 0.5

    return round(base, 2)


# === PUBLISH SENSOR DATA TO MQTT TOPICS ===
def publish_sensor_data(client):
    """
    Loads buildings data and publishes simulated sensor readings
    for both university and accommodation buildings.
    """
    file_path = os.path.join(basedir, 'static', 'buildings_data.json')
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            university_buildings = data.get('university_buildings', [])
            accommodation_buildings = data.get('accommodation_buildings', [])
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        university_buildings = []
        accommodation_buildings = []

    # Publish data for university buildings
    for building in university_buildings:
        publish_data(client, building, 'electricity', None)
        publish_data(client, building, 'gas', None)

    # Publish data for each flat in accommodation buildings
    for building in accommodation_buildings:
        total_flats = building.get('total_flats', 0)
        for flat_number in range(1, total_flats + 1):
            flat_building_name = f"{building['building']} Flat {flat_number}"
            publish_data(client, building, 'electricity', flat_building_name)
            publish_data(client, building, 'gas', flat_building_name)


# === BUILD AND PUBLISH A SINGLE MESSAGE ===
def publish_data(client, building, sensor_type, flat_number):
    """Publish a single sensor reading for a building or flat."""
    timestamp = datetime.now(timezone.utc).isoformat()
    value = generate_reading(sensor_type)

    if building.get('is_accommodation'):
        zone = ''
        building_name = flat_number
    else:
        zone = building.get('zone')
        building_name = building['building']

    payload = create_payload(building, building_name, value, timestamp, zone)
    topic = TOPIC_ELECTRICITY if sensor_type == 'electricity' else TOPIC_GAS
    client.publish(topic, json.dumps(payload))

    logger.info(f"Published {sensor_type} data for {building['building']}.")


# === CREATE PAYLOAD STRUCTURE FOR SENSOR MESSAGE ===
def create_payload(building, building_name, value, timestamp, zone=""):
    """Returns a dictionary to be published as JSON payload."""
    return {
        "timestamp": timestamp,
        "building": building_name if building.get('is_accommodation') else f"{building['building']}",
        "building_code": building.get("building_code", ""),
        "zone": zone,
        "value": value
    }


# === MQTT CALLBACK: ON CONNECT ===
def on_connect(client, userdata, flags, rc):
    """Called when client connects to the broker."""
    logger.info(f"Connected to MQTT broker with result code {rc}")
    client.subscribe(TOPIC_ELECTRICITY)
    client.subscribe(TOPIC_GAS)


# === MQTT CALLBACK: ON MESSAGE RECEIVED ===
def on_message(client, userdata, msg, app):
    """
    Called when a message is received. Parses and stores it in DB batch.
    """
    payload = json.loads(msg.payload)
    timestamp = payload['timestamp']
    building = payload['building']
    building_code = payload['building_code']
    zone = payload['zone']
    value = payload['value']
    category = 'electricity' if msg.topic == TOPIC_ELECTRICITY else 'gas'

    reading = EnergyReading(
        timestamp=datetime.fromisoformat(timestamp.replace("Z", "+00:00")),
        building=building,
        building_code=building_code,
        zone=zone,
        value=value,
        category=category
    )

    # Add to batch
    readings_to_add.append(reading)

    # Commit if batch limit reached
    if len(readings_to_add) >= BATCH_SIZE:
        with app.app_context():
            db.session.add_all(readings_to_add)
            db.session.commit()
            logger.debug(f"Committed {BATCH_SIZE} readings to the database.")
            readings_to_add.clear()


# === FINAL COMMIT FOR LEFTOVER READINGS ===
def commit_remaining_readings(app):
    """Commit any remaining readings in the batch list."""
    with app.app_context():
        if readings_to_add:
            db.session.add_all(readings_to_add)
            db.session.commit()
            logger.debug(f"Committed remaining {len(readings_to_add)} readings to the database.")
            readings_to_add.clear()


# === BACKGROUND THREAD TO RUN SIMULATION ===
def simulator_thread(app):
    """
    Launches MQTT client in a background thread:
    - Listens to messages
    - Publishes simulated data at intervals
    """
    logger.info("Background thread started.")
    client = connect_mqtt()

    # Set MQTT event handlers
    client.on_connect = on_connect
    client.on_message = lambda c, u, m: on_message(c, u, m, app)  # Capture Flask app context

    # Start MQTT loop (non-blocking)
    client.loop_start()

    # Repeatedly publish data and commit remaining readings
    while True:
        publish_sensor_data(client)
        logger.info(f"Waiting {PUBLISH_INTERVAL} seconds for next publish...")
        time.sleep(PUBLISH_INTERVAL)
        commit_remaining_readings(app)
