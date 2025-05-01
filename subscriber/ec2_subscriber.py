import os
import json
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import mysql.connector
from datetime import datetime

# AWS IoT Core Configuration
ENDPOINT = "axpjfhduaw82h-ats.iot.ap-south-1.amazonaws.com"
CLIENT_ID = "angad_subscriber"
TOPIC = "vehicle/data"

# Absolute Paths to Certificates
ROOT_CA = os.path.abspath("AmazonRootCA1.pem")
PRIVATE_KEY = os.path.abspath("private.key")
CERTIFICATE = os.path.abspath("device certificate.crt")

# MySQL Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "iot_user",
    "password": "Mycloud@25",  # Replace with your real password
    "database": "vehicle_data"
}

# Connect to MySQL
def connect_to_db():
    while True:
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            print("✅ Connected to MySQL database.")
            return conn
        except mysql.connector.Error as err:
            print(f"❌ MySQL Error: {err}")
            time.sleep(5)

db = connect_to_db()
cursor = db.cursor()

# MQTT Client Setup
mqtt_client = AWSIoTMQTTClient(CLIENT_ID)
mqtt_client.configureEndpoint(ENDPOINT, 8883)
mqtt_client.configureCredentials(ROOT_CA, PRIVATE_KEY, CERTIFICATE)

# Callback Function to Handle Incoming Messages
def message_callback(client, userdata, message):
    try:
        print(f"Raw Message Payload: {message.payload}")
        data = json.loads(message.payload)
        print(f"Parsed Data: {data}")

        vehicle_id = data.get("vehicle_ID")
        speed = data.get("Speed")
        timestamp_str = data.get("timestamp")
        location = data.get("location")

        # Convert timestamp to standard datetime format (if needed)
        timestamp = datetime.strptime(timestamp_str, "%d/%m/%Y %H:%M:%S IST")

        sql = """
        INSERT INTO vehicle_status (vehicle_id, speed, timestamp, location)
        VALUES (%s, %s, %s, %s)
        """
        values = (vehicle_id, speed, timestamp, location)
        cursor.execute(sql, values)
        db.commit()

        print(f"✅ Stored: {vehicle_id} | Speed: {speed} | Time: {timestamp_str} | Location: {location}")

    except Exception as e:
        print(f"❌ Error processing message: {e}")

# Subscribe and Start Listening
def connect_mqtt():
    try:
        mqtt_client.connect()
        print(f"✅ Connected to AWS IoT. Subscribed to topic: {TOPIC}")
        mqtt_client.subscribe(TOPIC, 1, message_callback)
    except Exception as e:
        print(f"❌ MQTT Error: {e}")
        time.sleep(5)
        connect_mqtt()

connect_mqtt()

# Keep the Subscriber Running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("🛑 Shutting down subscriber...")
    cursor.close()
    db.close()
    mqtt_client.disconnect()
    print("✅ Disconnected.")
