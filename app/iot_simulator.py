import json
import os
import random
import time
from datetime import datetime

import paho.mqtt.client as mqtt

from app import logger, app
from app.extensions import db
from app.models import EnergyReading

# MQTT Setup
BROKER = 'localhost'
PORT = 1883
TOPIC_ELECTRICITY = 'uob/electricity'
TOPIC_GAS = 'uob/gas'
PUBLISH_INTERVAL = 300  # 5 minutes in seconds
# Set a batch size limit to avoid memory overflow
BATCH_SIZE = 200

# Global variable to hold readings temporarily
readings_to_add = []

basedir = os.path.abspath(os.path.dirname(__file__))

# Connect to MQTT Broker
def connect_mqtt():
    client = mqtt.Client()
    client.connect(BROKER, PORT)
    return client

# Generate realistic reading
def generate_reading(sensor_type):
    now = datetime.now()
    hour = now.hour
    weekday = now.weekday()  # 0 = Monday, 6 = Sunday

    if sensor_type == 'electricity':
        if 8 <= hour < 18:
            base = random.uniform(300, 600)
        else:
            base = random.uniform(50, 200)
        if weekday >= 5:
            base *= 0.6
    elif sensor_type == 'gas':
        if 8 <= hour < 18:
            base = random.uniform(20, 50)
        else:
            base = random.uniform(5, 20)
        if weekday >= 5:
            base *= 0.5

    return round(base, 2)

# Publish data
def publish_sensor_data(client):
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

    # Publish data for accommodation buildings (iterate over flats)
    for building in accommodation_buildings:
        total_flats = building.get('total_flats', 0)
        for flat_number in range(1, total_flats + 1):
            flat_building_name = f"{building['building']} Flat {flat_number}"
            publish_data(client, building, 'electricity', flat_building_name)
            publish_data(client, building, 'gas', flat_building_name)

# Publish data for a building or flat
def publish_data(client, building, sensor_type, flat_number):
    timestamp = datetime.now(datetime.timezone.utc)
    value = generate_reading(sensor_type)
    if building.get('is_accommodation') == True:
        zone = ''
        building_name = flat_number

    else:
        zone = building.get('zone')
        building_name = building['building']

    payload = create_payload(building, building_name, value, timestamp, zone)
    topic = TOPIC_ELECTRICITY if sensor_type == 'electricity' else TOPIC_GAS
    client.publish(topic, json.dumps(payload))

    logger.info(f"Published {sensor_type} data for {building['building']}.")

# Function to create payload for electricity or gas data
def create_payload(building, building_name, value, timestamp, zone=""):
    return {
        "timestamp": timestamp,
        "building": building_name if building.get('is_accommodation') else f"{building['building']}",
        "building_code": building.get("building_code", ""),
        "zone": zone if zone else "",
        "value": value
    }
# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    logger.info(f"Connected to MQTT broker with result code {rc}")
    client.subscribe(TOPIC_ELECTRICITY)
    client.subscribe(TOPIC_GAS)

# Callback when a message is received
def on_message(client, userdata, msg):
    payload = json.loads(msg.payload)
    timestamp = payload['timestamp']
    building = payload['building']
    building_code = payload['building_code']
    zone = payload['zone']
    value = payload['value']

    # Determine category based on the topic
    category = 'electricity' if msg.topic == TOPIC_ELECTRICITY else 'gas'

    # Create the reading object
    reading = EnergyReading(
        timestamp=datetime.fromisoformat(timestamp),
        building=building,
        building_code=building_code,
        zone=zone,
        value=value,
        category=category
    )

    # Add the reading to the list
    readings_to_add.append(reading)

    # Commit the batch when the batch size limit is reached
    if len(readings_to_add) >= BATCH_SIZE:
        with app.app_context():
            db.session.add_all(readings_to_add)
            db.session.commit()
            logger.debug(f"Committed {BATCH_SIZE} readings to the database.")
            readings_to_add.clear()  # Clear the list after committing

#Commit any remaining readings after processing all messages
def commit_remaining_readings():
    with app.app_context():
        if readings_to_add:
            db.session.add_all(readings_to_add)
            db.session.commit()
            logger.debug(f"Committed remaining {len(readings_to_add)} readings to the database.")
            readings_to_add.clear()

# Background thread to run the simulator and consume messages
def simulator_thread():
    logger.info("Background thread started.")
    client = connect_mqtt()

    # Assign callbacks
    client.on_connect = on_connect
    client.on_message = on_message

    # Start the MQTT loop in the background, which will handle both subscribing and publishing
    client.loop_start()

    # Publish sensor data every PUBLISH_INTERVAL seconds
    while True:
        publish_sensor_data(client)
        logger.info(f"Waiting {PUBLISH_INTERVAL} seconds for next publish...")
        time.sleep(PUBLISH_INTERVAL)
