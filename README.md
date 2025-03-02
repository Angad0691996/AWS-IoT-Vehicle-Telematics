# AWS-IoT-Vehicle-Telematics
🚗 Vehicle Telematics Cloud Integration – Project Overview
Description - 
This project enables real-time vehicle telemetry data collection, storage, and visualization using AWS IoT Core, MySQL, and Grafana. Every 5 seconds, vehicle sensors transmit key parameters (GPS, speed, fuel level, RPM, battery voltage, and more) to AWS IoT Core using the MQTT protocol. The data is then processed and stored in a MySQL database hosted on an AWS EC2 instance.

For data visualization, Grafana is deployed on the cloud to provide real-time insights into vehicle performance, diagnostics, and driver behavior. The system allows for future enhancements, including predictive maintenance, anomaly detection, and AI-driven analytics

Vehicle IoT Edge Device(Raspberry Pi) → AWS IoT Core → EC2 (MySQL) → Grafana Dashboard
