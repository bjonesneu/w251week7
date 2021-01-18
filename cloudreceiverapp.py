import paho.mqtt.client as mqtt
import boto3
import json
import uuid
import sys

# Setup connection to local broker
LOCAL_MQTT_HOST="mqbroker"
LOCAL_MQTT_PORT=1883
LOCAL_MQTT_TOPIC="tst011235"

def on_connect_local(client, userdata, flags, rc):
    if rc==0:
        client.connected = True
        print("Connected to local broker with rc: " + str(rc))
        client.subscribe(LOCAL_MQTT_TOPIC)
        print("Subscribed to topic",LOCAL_MQTT_TOPIC)
    else:
        print("Connection error")

# Setup action when message received on subscribe channel
# to save to S3
def on_message(client,userdata, msg):
  try:
    print("Message received")

    # save received message to S3
    data = json.loads(msg.payload)
    #print(data)
    obj_key = data['id'] # use str(uuid.uuid4()) to generate new key
    s3 = boto3.client('s3')
    response = s3.put_object(Bucket='w251week3', Body=msg.payload, Key=obj_key)
    print('File saved to S3.')
  except:
      print("Error saving to S3:", sys.exc_info())

local_mqttclient = mqtt.Client()
local_mqttclient.on_connect = on_connect_local
local_mqttclient.on_message = on_message
local_mqttclient.connected = False
local_mqttclient.connect(LOCAL_MQTT_HOST, LOCAL_MQTT_PORT, 60)


# Start running the app
local_mqttclient.loop_forever()

