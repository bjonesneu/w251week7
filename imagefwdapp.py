import paho.mqtt.client as mqtt
import time
import json
import sys
from threading import Thread
import os

CLOUD_MQTT_HOST = os.getenv('CLOUD_MQTT_HOST')
CLOUD_MQTT_PORT = os.getenv('CLOUD_MQTT_PORT')
#print(CLOUD_MQTT_HOST, CLOUD_MQTT_PORT)
if not CLOUD_MQTT_HOST or not CLOUD_MQTT_PORT:
    print('Set environment variable CLOUD_MQTT_HOST before running this program.')
    exit

# Setup general methods for broker connection
def connect_broker(client):
    # retry connection every 3 seconds
    if not client.connected:
        print("Trying to connect to "+client.label+" broker...")
        try:
            client.connect(client.MQTT_HOST, client.MQTT_PORT, 60)
        except:
            print('Error connecting to ' + client.label + " broker. Retrying in 3 seconds.")

        if client.label=="local":
            client.loop_forever()
        else:
            client.loop_start()
        
        time.sleep(3)
        connect_broker(client)

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected = True
        print("Connected to " + client.label + " broker with rc: " + str(rc))
        
        if client.label == "local":
            client.subscribe(client.MQTT_TOPIC)
            print("Subscribed to topic",client.MQTT_TOPIC)
    else:
        print("Connection error")

def on_disconnect(client, userdata, rc):
    print("Disconnected from " + client.label + " broker with rc: " + str(rc))
    client.connected = False

# Setup connection to local broker

# Setup action when message received on subscribe channel
def on_message(client,userdata, msg):
  try:
    print("Message received")
    #print("data",userdata,msg)
    
    # republish received message to cloud
    content = msg.payload
    #print(content)
    if client.cloud_client.connected:
        client.cloud_client.publish(client.cloud_client.MQTT_TOPIC, payload=content, qos=1, retain=False)
        print('Cloud broker connected, message forwarded.')
    else:
        print('Cloud broker not connected, could not forward message.')
  except:
      print("Error forwarding to cloud broker:", sys.exc_info())

local_mqttclient = mqtt.Client()
local_mqttclient.label = "local"
local_mqttclient.on_connect = on_connect
local_mqttclient.on_disconnect = on_disconnect
local_mqttclient.on_reconnect = on_connect
local_mqttclient.on_message = on_message
local_mqttclient.connected = False
local_mqttclient.MQTT_HOST="mqbroker"
local_mqttclient.MQTT_PORT=1883
local_mqttclient.MQTT_TOPIC="faces"

# Setup connection to cloud broker
cloud_mqttclient = mqtt.Client()
cloud_mqttclient.label = "cloud"
cloud_mqttclient.on_connect = on_connect
cloud_mqttclient.on_disconnect = on_disconnect
cloud_mqttclient.on_reconnect = on_connect
cloud_mqttclient.connected = False
cloud_mqttclient.MQTT_HOST=CLOUD_MQTT_HOST
cloud_mqttclient.MQTT_PORT=int(CLOUD_MQTT_PORT)
cloud_mqttclient.MQTT_TOPIC="tst011235"

# Connect the two brokers with each other
cloud_mqttclient.local_client = local_mqttclient
local_mqttclient.cloud_client = cloud_mqttclient

# Start connection to the cloud broker
th_cloud_connect = Thread(target=connect_broker(cloud_mqttclient))
th_cloud_connect.start()

# Start running the app
th_local_connect = Thread(target=connect_broker(local_mqttclient))
th_local_connect.start()

