import numpy as np
import cv2 as cv
import uuid
import paho.mqtt.client as mqtt

# Setup connection to MQTT broker to publish detected faces
LOCAL_MQTT_HOST="mqbroker"
LOCAL_MQTT_PORT=1883
LOCAL_MQTT_TOPIC="faces"

def on_connect_local(client, userdata, flags, rc):
    if rc==0:
        client.connected = True
        print("Connected to local broker with rc: " + str(rc))
    else:
        print("Connection error")
        client.connected = False

def on_disconnect_local(client, userdata, rc):
    print("Disconnected from local broker with rc: " + str(rc))
    client.connected = False

print("Setting up connection to broker")
local_mqttclient = mqtt.Client("facedetector")
local_mqttclient.on_connect = on_connect_local
local_mqttclient.on_disconnect = on_disconnect_local
local_mqttclient.on_reconnect = on_connect_local
local_mqttclient.connected = False
local_mqttclient.connect(LOCAL_MQTT_HOST, LOCAL_MQTT_PORT, 60)
local_mqttclient.loop_start()

# Setup connection to camera

# The argument 0 corresponds to /dev/video0, the first found camera.  In this case it is the USB camera.
cap = cv.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Remove color information to compact data
    frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    # Display the resulting frame
    #cv.imshow('frame',frame_gray)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

    if True:
        # face detection and other logic goes here
        face_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')

        faces = face_cascade.detectMultiScale(frame_gray, 1.3, 5)
        for (x,y,w,h) in faces:
            print('Face detected at', x, y, w, h, ", broker connected:", local_mqttclient.connected)
            cv.rectangle(frame_gray, (x, y), (x+w, y+h), (255, 255, 255), 2)
            face = frame_gray[y:y+h,x:x+w]
            #cv.imshow('frame',face)
            # cut out face from the frame... 
            rc,png = cv.imencode('.png', face)
            if local_mqttclient.connected:
                #print("Trying to publish")
                msg = png.tobytes()
                msg = "Test message from local (" + str(x) + ", " + str(y) + ")"
                rc = local_mqttclient.publish(LOCAL_MQTT_TOPIC, payload=msg, qos=1, retain=False)
                print("\tPublished face with rc = ",rc)

    #cv.imshow('frame',frame_gray)

# When everything done, release all resources:  display, camera and mqtt
cap.release()
cv.destroyAllWindows()
local_mqttclient.loop_stop()

