import os
import random  # Import the random module
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import time

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

# Function to Generate Random Vehicle Data
def generate_vehicle_data():
    return {
        "vehicle_id": "ANGAD123",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "vehicle_status": {
            "model": "Tesla Model S",
            "make": "Tesla",
            "year": "2025",
            "odometer": random.randint(5000, 200000),  # Odometer reading
            "mode": random.choice(["Idle", "Moving", "Parked", "Off"])
        },
        "location": {
            "latitude": round(random.uniform(-90, 90), 6),
            "longitude": round(random.uniform(-180, 180), 6),
            "altitude": round(random.uniform(0, 5000), 2),
            "speed": random.randint(0, 120),  # Speed in km/h
            "heading": random.choice(["North", "South", "East", "West"]),
            "trip_distance": round(random.uniform(0, 500), 2)
        },
        "engine_performance": {
            "rpm": random.randint(800, 6000),
            "throttle_position": random.randint(0, 100),
            "fuel_level": random.randint(0, 100),
            "fuel_consumption": round(random.uniform(5, 15), 2),  # L/100km
            "battery_voltage": round(random.uniform(11.5, 14.8), 2),
            "oil_pressure": round(random.uniform(20, 100), 2),
            "coolant_temperature": random.randint(60, 120)
        },
        "diagnostics": {
            "check_engine_light": random.choice([True, False]),
            "obd_codes": random.choices(["P0300", "P0420", "P0171", "P0455"], k=random.randint(0, 2)),
            "brake_wear": random.randint(50, 100),
            "tire_pressure": {
                "front_left": random.randint(28, 36),
                "front_right": random.randint(28, 36),
                "rear_left": random.randint(28, 36),
                "rear_right": random.randint(28, 36)
            },
            "transmission_status": random.choice(["Drive", "Neutral", "Reverse", "Park"])
        },
        "environment": {
            "outside_temperature": random.randint(-10, 45),
            "road_condition": random.choice(["Dry", "Wet", "Icy", "Snowy"]),
            "weather": random.choice(["Sunny", "Cloudy", "Rainy", "Stormy", "Snowy"])
        },
        "driver_behavior": {
            "harsh_acceleration": random.choice([True, False]),
            "harsh_braking": random.choice([True, False]),
            "cornering_gforce": round(random.uniform(0.5, 2.5), 2),
            "seat_belt_status": random.choice(["Fastened", "Unfastened"]),
            "airbag_deployment": random.choice([True, False]),
            "fatigue_alert": random.choice([True, False])
        },
        "connectivity": {
            "network_signal": random.choice(["Excellent", "Good", "Weak", "No Signal"]),
            "data_transmission": random.choice(["Active", "Delayed", "Failed"]),
            "cloud_sync": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    }

# Publish Data Every 5 Seconds
# Loop to send random data continuously
while True:
    vehicle_data = generate_vehicle_data()
    payload = json.dumps(vehicle_data)
    mqtt_client.publish(TOPIC, payload, 1)
    print(f"Published: {payload}")

    time.sleep(5)  # Send data every 5 seconds

# Disconnect (if needed)
# mqtt_client.disconnect()
# print("Disconnected.")
