import paho.mqtt.client as mqtt  #import the client1
import time

# broker list
brokers=["iot.eclipse.org","broker.hivemq.com",\
         "test.mosquitto.org","192.168.8.167","139.162.222.115"]

broker=brokers[1]


def on_log(client, userdata, level, buf):
        print("log: "+buf)
def on_connect(client, userdata, flags, rc):
    if rc==0:
        print("connected OK")
    else:
        print("Bad connection Returned code=",rc)
def on_disconnect(client, userdata, flags, rc=0):
        print("DisConnected result code "+str(rc))
def on_message(client,userdata,msg):
        topic=msg.topic
        m_decode=str(msg.payload.decode("utf-8","ignore"))
        print("message received",m_decode)

client = mqtt.Client("IOT_pub_AVIV7235_LIEL9203", clean_session=True) # create new client instance

client.on_connect=on_connect  #bind call back function
client.on_disconnect=on_disconnect
client.on_log=on_log
client.on_message=on_message

    
print("Connecting to broker ",broker)
port=1883

client.will_set(
    "IOT/SMART_HOME/7235_9203/status",
    payload="Client disconnected unexpectedly",
    qos=1,
    retain=True
)

client.connect(broker, port, keepalive=90)    #connect to broker

pub_topic = "IOT/SMART_HOME/7235_9203/sensor1"

# Next 2 loops will publishing 40 messages to one topic(house) and 2 subtopics(sensor_0 and sensor_1)
client.publish(pub_topic, "Final test message", qos=1, retain=False)
# for j in range(2):
#         for i in range(20):
#              client.publish("matzi/house/sensor_"+str(j),"my  "+str(i)+" message")
#              print("Sent: 'my  "+str(i)+" message'" + " to: 'matzi/house/sensor_"+str(j)+"'")
#              time.sleep(1)
time.sleep(1)


print("End publish_client run script")

##client.loop_start()  #Start loop
### part for your change
##client.subscribe("house/sensor1")
##client.publish("house/sensor1","my first message")
##
##time.sleep(2)
##client.loop_stop()    #Stop loop 
client.disconnect() # disconnect
