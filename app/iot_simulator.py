import os

from flask import Flask
import threading
import time
import random
import json
from datetime import datetime
import paho.mqtt.client as mqtt

from app import db, app
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
def generate_reading(building_name, sensor_type):
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
    file_path = os.path.join(basedir, 'static', 'building_data.json')
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            buildings = data.get('buildings', [])
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        buildings = []

    for b in buildings:
        timestamp = datetime.utcnow().isoformat()

        # Electricity
        elec_value = generate_reading(b['building'], 'electricity')
        elec_payload = {
            "timestamp": timestamp,
            "building": b['building'],
            "building_code": b['building_code'],
            "zone": b['zone'],
            "value": elec_value
        }
        client.publish(TOPIC_ELECTRICITY, json.dumps(elec_payload))
        print(f"Published electricity data for {b['building']}.")

        # Gas
        gas_value = generate_reading(b['building'], 'gas')
        gas_payload = {
            "timestamp": timestamp,
            "building": b['building'],
            "building_code": b['building_code'],
            "zone": b['zone'],
            "value": gas_value
        }
        client.publish(TOPIC_GAS, json.dumps(gas_payload))
        print(f"Published gas data for {b['building']}.")


# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
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
            print(f"Committed {BATCH_SIZE} readings to the database.")
            readings_to_add.clear()  # Clear the list after committing

#Commit any remaining readings after processing all messages
def commit_remaining_readings():
    with app.app_context():
        if readings_to_add:
            db.session.add_all(readings_to_add)
            db.session.commit()
            print(f"Committed remaining {len(readings_to_add)} readings to the database.")
            readings_to_add.clear()

# Background thread to run the simulator and consume messages
def simulator_thread():
    print("Background thread started.")
    client = connect_mqtt()

    # Assign callbacks
    client.on_connect = on_connect
    client.on_message = on_message

    # Start the MQTT loop in the background, which will handle both subscribing and publishing
    client.loop_start()

    # Publish sensor data every PUBLISH_INTERVAL seconds
    while True:
        publish_sensor_data(client)
        print(f"Waiting {PUBLISH_INTERVAL} seconds for next publish...")
        time.sleep(PUBLISH_INTERVAL)
