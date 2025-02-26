import os
import json
import mysql.connector
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# AWS IoT Core Details
ENDPOINT = "axpjfhduaw82h-ats.iot.ap-south-1.amazonaws.com"
CLIENT_ID = "angad_subscriber"
TOPIC = "vehicle/data"

# MySQL Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "iot_user",
    "password": "Mycloud@25",  # Replace with your MySQL password
    "database": "vehicle_data"
}

# Absolute Paths to Certificates
ROOT_CA = os.path.abspath("AmazonRootCA1.pem")
PRIVATE_KEY = os.path.abspath("private.key")
CERTIFICATE = os.path.abspath("device_certificate.crt")

# Function to establish a MySQL connection
def connect_to_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("✅ Connected to MySQL database.")
        return conn
    except mysql.connector.Error as err:
        print(f"\n❌ MySQL Connection Error: {err}")
        time.sleep(5)
        return connect_to_db()  # Retry connection

# Establish the database connection
db = connect_to_db()
cursor = db.cursor()

# Initialize MQTT Client
mqtt_client = AWSIoTMQTTClient(CLIENT_ID)
mqtt_client.configureEndpoint(ENDPOINT, 8883)
mqtt_client.configureCredentials(ROOT_CA, PRIVATE_KEY, CERTIFICATE)

# Callback function when message is received
def message_callback(client, userdata, message):
    try:
        data = json.loads(message.payload)

        # Extract fields from JSON
        vehicle_id = data.get("vehicle_id", "Unknown")
        timestamp = data.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S"))

        vehicle_status = data.get("vehicle_status", {})
        model = vehicle_status.get("model", "Unknown")
        make = vehicle_status.get("make", "Unknown")
        year = vehicle_status.get("year", 0)
        odometer = vehicle_status.get("odometer", 0)
        mode = vehicle_status.get("mode", "Unknown")

        location = data.get("location", {})
        latitude = location.get("latitude", 0.0)
        longitude = location.get("longitude", 0.0)
        altitude = location.get("altitude", 0.0)
        speed = location.get("speed", 0)
        heading = location.get("heading", "Unknown")
        trip_distance = location.get("trip_distance", 0.0)

        engine_performance = data.get("engine_performance", {})
        rpm = engine_performance.get("rpm", 0)
        throttle_position = engine_performance.get("throttle_position", 0)
        fuel_level = engine_performance.get("fuel_level", 0)
        fuel_consumption = engine_performance.get("fuel_consumption", 0.0)
        battery_voltage = engine_performance.get("battery_voltage", 0.0)
        oil_pressure = engine_performance.get("oil_pressure", 0.0)
        coolant_temperature = engine_performance.get("coolant_temperature", 0)

        diagnostics = data.get("diagnostics", {})
        check_engine_light = diagnostics.get("check_engine_light", False)
        obd_codes = json.dumps(diagnostics.get("obd_codes", []))  # Store as JSON string
        brake_wear = diagnostics.get("brake_wear", 0)
        tire_pressure = json.dumps(diagnostics.get("tire_pressure", {}))  # Store as JSON string
        transmission_status = diagnostics.get("transmission_status", "Unknown")

        environment = data.get("environment", {})
        outside_temperature = environment.get("outside_temperature", 0)
        road_condition = environment.get("road_condition", "Unknown")
        weather = environment.get("weather", "Unknown")

        driver_behavior = data.get("driver_behavior", {})
        harsh_acceleration = driver_behavior.get("harsh_acceleration", False)
        harsh_braking = driver_behavior.get("harsh_braking", False)
        cornering_gforce = driver_behavior.get("cornering_gforce", 0.0)
        seat_belt_status = driver_behavior.get("seat_belt_status", "Unknown")
        airbag_deployment = driver_behavior.get("airbag_deployment", False)
        fatigue_alert = driver_behavior.get("fatigue_alert", False)

        connectivity = data.get("connectivity", {})
        network_signal = connectivity.get("network_signal", "Unknown")
        data_transmission = connectivity.get("data_transmission", "Unknown")
        cloud_sync = connectivity.get("cloud_sync", time.strftime("%Y-%m-%d %H:%M:%S"))

        full_data = json.dumps(data)  # Store entire JSON payload


        # Insert data into MySQL
        sql = """
        INSERT INTO telemetry (vehicle_id, timestamp, model, make, year, odometer, mode,
           latitude, longitude, altitude, speed, heading, trip_distance,
            rpm, throttle_position, fuel_level, fuel_consumption, battery_voltage, oil_pressure, coolant_temperature,
           check_engine_light, obd_codes, brake_wear, tire_pressure, transmission_status,
          outside_temperature, road_condition, weather,
            harsh_acceleration, harsh_braking, cornering_gforce, seat_belt_status, airbag_deployment, fatigue_alert,
            network_signal, data_transmission, cloud_sync, full_data)
        VALUES (
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s
        )
        """

        values = (
            vehicle_id, timestamp, model, make, year, odometer, mode,
            latitude, longitude, altitude, speed, heading, trip_distance,
            rpm, throttle_position, fuel_level, fuel_consumption, battery_voltage, oil_pressure, coolant_temperature,
            check_engine_light, obd_codes, brake_wear, tire_pressure, transmission_status,
            outside_temperature, road_condition, weather,
            harsh_acceleration, harsh_braking, cornering_gforce, seat_belt_status, airbag_deployment, fatigue_alert,
            network_signal, data_transmission, cloud_sync, full_data
        )



        cursor.execute(sql, values)
        db.commit()

        print(f"\n✅ Data Stored in MySQL: {vehicle_id} @ {timestamp}")

    except Exception as e:
        print(f"\n❌ Error: {e}")

# Connect & Subscribe
def connect_mqtt():
    try:
        mqtt_client.connect()
        print(f"✅ Connected to AWS IoT Core. Subscribing to topic: {TOPIC}...")
        mqtt_client.subscribe(TOPIC, 1, message_callback)
    except Exception as e:
        print(f"\n❌ MQTT Connection Error: {e}")
        time.sleep(5)
        connect_mqtt()  # Retry connection

connect_mqtt()

# Keep listening for messages
try:
    while True:
        time.sleep(1)  # Prevent high CPU usage
except KeyboardInterrupt:
    print("\n🚪 Shutting down subscriber...")
    cursor.close()
    db.close()
    mqtt_client.disconnect()
    print("✅ Disconnected from MySQL & AWS IoT Core.")
