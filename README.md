# Smart Greenhouse IoT Monitoring System

This project simulates a Smart Greenhouse IoT system using MQTT, Python, PyQt5, and SQLite.

## Project Components

1. DHT Emulator  
   Simulates temperature and humidity sensor data.

2. Button Emulator  
   Simulates a manual button that sends a PRESSED message.

3. Relay Emulator  
   Simulates a relay/pump/fan and changes state according to ON/OFF commands.

4. Data Manager  
   Receives MQTT messages, analyzes sensor data, controls the relay, and saves measurements into SQLite database.

5. GUI Application  
   Displays real-time temperature, humidity, relay state, warning, and alarm messages.

## MQTT Broker

broker.hivemq.com  
Port: 1883

## MQTT Topics

greenhouse/sensors/dht  
greenhouse/control/button  
greenhouse/actuators/relay  
greenhouse/status/relay  
greenhouse/status/warning  
greenhouse/status/alarm  

## Rules

Temperature <= 30: NORMAL  
Temperature > 30: WARNING  
Temperature > 35: ALARM  
Humidity < 40: Relay ON  
Humidity >= 40: Relay OFF  
Button pressed: Toggle Relay ON/OFF 
## Installation

Install the required Python libraries:

```bash
py -m pip install -r requirements.txt 
```

## How to Run

Open 5 terminals and run:

```bash
py data_manager.py
py relay_emulator.py
py gui_app.py
py dht_emulator.py
py button_emulator.py
```
Click Enable/Connect in the emulator windows.

## Database

The SQLite database is created automatically when running data_manager.py.

Database file:

```text
smart_greenhouse.db
```