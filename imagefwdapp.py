import paho.mqtt.client as mqtt


# Setup connection to local broker
LOCAL_MQTT_HOST="mqbroker"
LOCAL_MQTT_PORT=1883
LOCAL_MQTT_TOPIC="faces"

def on_connect_local(client, userdata, flags, rc):
    if rc==0:
        client.connected = True
        print("Connected to local broker with rc: " + str(rc))
        client.subscribe(LOCAL_MQTT_TOPIC)
        print("Subsribed to topic",LOCAL_MQTT_TOPIC)
    else:
        print("Connection error")

# Setup action when message received on subscribe channel
def on_message(client,userdata, msg):
  try:
    print("Message received")
    #print("data",userdata,msg)
    
    # republish received message to cloud
    msg = msg.payload
    if client.cloud_client.connected:
        client.cloud_client.publish(CLOUD_MQTT_TOPIC, payload=msg, qos=1, retain=False)
        print('Cloud broker connected, message forwarded.')
    else:
        print('Cloud broker not connected, could not forward message.')
  except:
      print("Error publishing:", sys.exc_info()[0])

local_mqttclient = mqtt.Client()
local_mqttclient.on_connect = on_connect_local
local_mqttclient.on_message = on_message
local_mqttclient.connected = False
local_mqttclient.connect(LOCAL_MQTT_HOST, LOCAL_MQTT_PORT, 60)

# Setup connection to cloud broker
CLOUD_MQTT_HOST="broker.hivemq.com"
CLOUD_MQTT_PORT=1883
CLOUD_MQTT_TOPIC="tst011235"

def on_connect_cloud(client, userdata, flags, rc):
    if rc==0:
        client.connected = True
        print("Connected to cloud broker with rc: " + str(rc))
    else:
        print("Connection error")

cloud_mqttclient = mqtt.Client()
cloud_mqttclient.on_connect = on_connect_cloud
cloud_mqttclient.connected = False
local_mqttclient.cloud_client = cloud_mqttclient
cloud_mqttclient.connect(CLOUD_MQTT_HOST, CLOUD_MQTT_PORT, 60)

# Connect the two brokers
cloud_mqttclient.local_client = local_mqttclient
local_mqttclient.cloud_client = cloud_mqttclient

# Start connection to the cloud broker
cloud_mqttclient.loop_start()

# Start running the app
local_mqttclient.loop_forever()
