import json
import sqlite3
from datetime import datetime
import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883

TOPIC_DHT = "greenhouse/sensors/dht"
TOPIC_BUTTON = "greenhouse/control/button"
TOPIC_RELAY = "greenhouse/actuators/relay"
TOPIC_WARNING = "greenhouse/status/warning"
TOPIC_ALARM = "greenhouse/status/alarm"
TOPIC_RELAY_STATUS = "greenhouse/status/relay"

DB_NAME = "smart_greenhouse.db"

relay_state = "OFF"


def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            temperature REAL,
            humidity REAL,
            relay_state TEXT,
            system_status TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("Database is ready:", DB_NAME)


def save_measurement(temperature, humidity, relay_state, system_status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO measurements (timestamp, temperature, humidity, relay_state, system_status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        temperature,
        humidity,
        relay_state,
        system_status
    ))

    conn.commit()
    conn.close()
    print("Measurement saved to database")


def decide_status_and_relay(client, temperature, humidity):
    global relay_state

    if temperature > 35:
        system_status = "ALARM"
        client.publish(TOPIC_ALARM, "Temperature is very high")
        print("ALARM: Temperature is very high")

    elif temperature > 30:
        system_status = "WARNING"
        client.publish(TOPIC_WARNING, "Temperature is high")
        print("WARNING: Temperature is high")

    else:
        system_status = "NORMAL"
        print("System status is NORMAL")

    if humidity < 40:
        relay_state = "ON"
        client.publish(TOPIC_RELAY, "ON")
        client.publish(TOPIC_RELAY_STATUS, "ON")
        print("Humidity is low -> Relay ON")

    else:
        relay_state = "OFF"
        client.publish(TOPIC_RELAY, "OFF")
        client.publish(TOPIC_RELAY_STATUS, "OFF")
        print("Humidity is OK -> Relay OFF")

    return system_status


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Data Manager connected to MQTT Broker")

        client.subscribe(TOPIC_DHT)
        client.subscribe(TOPIC_BUTTON)

        print("Subscribed to:", TOPIC_DHT)
        print("Subscribed to:", TOPIC_BUTTON)
    else:
        print("Connection failed with code:", rc)


def on_message(client, userdata, msg):
    global relay_state

    topic = msg.topic
    message = msg.payload.decode("utf-8", "ignore")

    print("\nMessage received")
    print("Topic:", topic)
    print("Message:", message)

    if topic == TOPIC_DHT:
        try:
            data = json.loads(message)
            temperature = float(data["temperature"])
            humidity = float(data["humidity"])

            system_status = decide_status_and_relay(client, temperature, humidity)
            save_measurement(temperature, humidity, relay_state, system_status)

        except Exception as e:
            print("Error reading DHT data:", e)

    elif topic == TOPIC_BUTTON:
        if message == "PRESSED":
            if relay_state == "OFF":
                relay_state = "ON"
            else:
                relay_state = "OFF"

            client.publish(TOPIC_RELAY, relay_state)
            client.publish(TOPIC_RELAY_STATUS, relay_state)

            print("Button pressed -> Relay toggled to:", relay_state)


create_database()

client = mqtt.Client("Greenhouse_Data_Manager", clean_session=True)
client.on_connect = on_connect
client.on_message = on_message

print("Connecting Data Manager to broker...")
client.connect(BROKER, PORT, 60)

client.loop_forever()