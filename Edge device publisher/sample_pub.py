import os
import random
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import time
from datetime import datetime

# AWS IoT Core Details
ENDPOINT = "axpjfhduaw82h-ats.iot.ap-south-1.amazonaws.com"
CLIENT_ID = "angad_publisher"
TOPIC = "vehicle/data"

# Absolute Paths to Certificates
ROOT_CA = os.path.abspath("AmazonRootCA1.pem")
PRIVATE_KEY = os.path.abspath("private.key")
CERTIFICATE = os.path.abspath("device certificate.crt")

# Initialize MQTT Client
mqtt_client = AWSIoTMQTTClient(CLIENT_ID)
mqtt_client.configureEndpoint(ENDPOINT, 8883)
mqtt_client.configureCredentials(ROOT_CA, PRIVATE_KEY, CERTIFICATE)

# Connect to AWS IoT Core
mqtt_client.connect()
print("Connected to AWS IoT Core.")

# Function to Generate Custom Vehicle Payload
def generate_payload():
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S IST")
    location = f"{round(random.uniform(-90, 90), 6)}, {round(random.uniform(-180, 180), 6)}"
    return {
        "vehicle_ID": "Angad001",
        "Speed": random.randint(0, 120),
        "timestamp": timestamp,
        "location": location
    }

# Publish Data Every 5 Seconds
while True:
    vehicle_data = generate_payload()
    payload = json.dumps(vehicle_data)
    mqtt_client.publish(TOPIC, payload, 1)
    print(f"Published: {payload}")
    time.sleep(5)
