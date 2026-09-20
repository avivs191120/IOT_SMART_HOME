import sys
import json
import paho.mqtt.client as mqtt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal, QObject

BROKER = "broker.hivemq.com"
PORT = 1883

TOPIC_DHT = "greenhouse/sensors/dht"
TOPIC_RELAY_STATUS = "greenhouse/status/relay"
TOPIC_WARNING = "greenhouse/status/warning"
TOPIC_ALARM = "greenhouse/status/alarm"


class Communicator(QObject):
    dht_signal = pyqtSignal(str, str)
    relay_signal = pyqtSignal(str)
    warning_signal = pyqtSignal(str)
    alarm_signal = pyqtSignal(str)


class GreenhouseGUI(QWidget):

    def __init__(self):
        super().__init__()

        self.comm = Communicator()
        self.comm.dht_signal.connect(self.update_dht)
        self.comm.relay_signal.connect(self.update_relay)
        self.comm.warning_signal.connect(self.update_warning)
        self.comm.alarm_signal.connect(self.update_alarm)

        self.setWindowTitle("Smart Greenhouse GUI")
        self.setGeometry(500, 200, 400, 300)

        self.title = QLabel("Smart Greenhouse Monitoring System")
        self.title.setAlignment(Qt.AlignCenter)

        self.temperature_label = QLabel("Temperature: --")
        self.humidity_label = QLabel("Humidity: --")
        self.relay_label = QLabel("Relay: OFF")
        self.status_label = QLabel("System Status: NORMAL")
        self.message_label = QLabel("Last Message: --")

        self.relay_label.setStyleSheet("background-color: gray; padding: 8px;")
        self.status_label.setStyleSheet("background-color: lightgreen; padding: 8px;")

        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addWidget(self.temperature_label)
        layout.addWidget(self.humidity_label)
        layout.addWidget(self.relay_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.message_label)

        self.setLayout(layout)

        self.start_mqtt()

    def start_mqtt(self):
        self.client = mqtt.Client("Greenhouse_GUI_Client", clean_session=True)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        print("Connecting GUI to broker...")
        self.client.connect(BROKER, PORT, 60)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("GUI connected to MQTT Broker")

            client.subscribe(TOPIC_DHT)
            client.subscribe(TOPIC_RELAY_STATUS)
            client.subscribe(TOPIC_WARNING)
            client.subscribe(TOPIC_ALARM)

            print("GUI subscribed to topics")
        else:
            print("GUI connection failed:", rc)

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        message = msg.payload.decode("utf-8", "ignore")

        print("GUI received:", topic, message)

        if topic == TOPIC_DHT:
            try:
                data = json.loads(message)
                temp = str(data["temperature"])
                hum = str(data["humidity"])
                self.comm.dht_signal.emit(temp, hum)
            except Exception as e:
                print("GUI error reading DHT:", e)

        elif topic == TOPIC_RELAY_STATUS:
            self.comm.relay_signal.emit(message)

        elif topic == TOPIC_WARNING:
            self.comm.warning_signal.emit(message)

        elif topic == TOPIC_ALARM:
            self.comm.alarm_signal.emit(message)

    def update_dht(self, temp, hum):
        self.temperature_label.setText("Temperature: " + temp + " °C")
        self.humidity_label.setText("Humidity: " + hum + " %")

    def update_relay(self, state):
        self.relay_label.setText("Relay: " + state)

        if state == "ON":
            self.relay_label.setStyleSheet("background-color: red; padding: 8px;")
        else:
            self.relay_label.setStyleSheet("background-color: gray; padding: 8px;")

    def update_warning(self, message):
        self.status_label.setText("System Status: WARNING")
        self.status_label.setStyleSheet("background-color: yellow; padding: 8px;")
        self.message_label.setText("Last Message: " + message)

    def update_alarm(self, message):
        self.status_label.setText("System Status: ALARM")
        self.status_label.setStyleSheet("background-color: red; padding: 8px;")
        self.message_label.setText("Last Message: " + message)


app = QApplication(sys.argv)
window = GreenhouseGUI()
window.show()
app.exec_()