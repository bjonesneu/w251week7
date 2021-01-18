import numpy as np
import cv2 as cv
import uuid
import time
import json
from threading import Thread
import paho.mqtt.client as mqtt

# Setup connection to MQTT broker to publish detected faces
LOCAL_MQTT_TOPIC="faces"

def connect_broker(client):
    # retry connection every 3 seconds
    if not client.connected:
        try:
            client.connect(client.MQTT_HOST, client.MQTT_PORT, 60)
        except:
            print('Error connecting to ' + client.label + " broker. Retrying in 3 seconds.") 

        client.loop_start()
        time.sleep(3)
        connect_broker(client)

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected = True
        print("Connected to " + client.label + " broker with rc: " + str(rc))
    else:
        print("Connection error")
        client.connected = False

def on_disconnect(client, userdata, rc):
    print("Disconnected from " + client.label + " broker with rc: " + str(rc))
    client.connected = False

print("Setting up connection to local broker")
local_mqttclient = mqtt.Client("facedetector")
local_mqttclient.on_connect = on_connect
local_mqttclient.on_disconnect = on_disconnect
local_mqttclient.on_reconnect = on_connect
local_mqttclient.connected = False
local_mqttclient.label = "local"
local_mqttclient.MQTT_HOST = "mqbroker"
local_mqttclient.MQTT_PORT = 1883

th_local_connect = Thread(target=connect_broker(local_mqttclient))
th_local_connect.start()

# Setup connection to camera

# The argument 0 corresponds to /dev/video0, the first found camera.  In this case it is the USB camera.
cap = cv.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Remove color information to compact data
    frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    # Display the resulting frame
    #cv.imshow('frame',frame_gray) # for interactive debugging

    if True:  # debugging switch
        # face detection and other logic goes here
        face_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')

        faces = face_cascade.detectMultiScale(frame_gray, 1.3, 5)
        for (x,y,w,h) in faces:
            print('Face detected at', x, y, w, h, ", broker connected:", local_mqttclient.connected)
            cv.rectangle(frame_gray, (x, y), (x+w, y+h), (255, 255, 255), 2)
            face = frame_gray[y:y+h,x:x+w] # extract data for detected face from frame
            #cv.imshow('frame',face)  # for dev/debugging
            rc,png = cv.imencode('.png', face)
            if local_mqttclient.connected:
                #print("Trying to publish")
                #msg = png.tobytes() # for dev/debugging
                #msg = "Test message from local (" + str(x) + ", " + str(y) + ")" # for dev/debugging
                msg = { "id": str(uuid.uuid4()),
                        "face": png.tolist()#.tobytes()
                        }
                #print(msg)
                rc = local_mqttclient.publish(LOCAL_MQTT_TOPIC, payload=json.dumps(msg), qos=1, retain=False)
                print("\tPublished face with rc = ",rc)

# When everything done, release all resources:  display, camera and mqtt
cap.release()
cv.destroyAllWindows()
local_mqttclient.loop_stop()

