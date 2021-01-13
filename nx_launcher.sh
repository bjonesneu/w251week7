#!/bin/bash

docker network create --driver bridge hw03
docker run --rm --name mqbroker --network hw03 -p 1883:1883 -d mqttbroker /usr/sbin/mosquitto
docker run --rm -v /usr/src/w251week3:/src --name imagefwdclient --network hw03 -d mqttclient python3 /src/imagefwdapp.py
docker run --privileged --rm --name facedetectapp -v /usr/src/w251week3:/src -v /data:/data -e DISPLAY -v /tmp:/tmp  --network hw03 -d opencvclient python3 /src/facedetectapp.py 
