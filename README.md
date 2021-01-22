# Homework 3 - class W251

## Introduction

The purpose of this homework is to build a lightweight IoT application pipeline with components on an edge device and in the cloud.  The basic functionality includes:

- detecting faces using camera on edge device
- publishing detected faces to messaging pipeline
- pushing messages from the edge device to a cloud platform
- storing files received on cloud platform to S3

The results of this assignment are available at:

- Code repository:  https://github.com/bjonesneu/w251week3.git
- Face repository:  https://s3.console.aws.amazon.com/s3/buckets/w251week3?region=us-east-2&tab=objects

## Solution

### Overview

Per the homework requirements, 5 containers were built and used for this project:

- Edge Device
1) App to detect and publish faces
2) Message Broker
3) App to push messages to cloud

- Cloud
4) Message Broker
5) App to store files on S3

(diagram)


### Key tech used
- Alpine Linux - lightweight OS
- OpenCV - Python library used for face detection
- MQTT - for message broker
- Paho - MQTT library for Python
- Boto3 - AWS library for Python
- Docker

The Face Detection app container uses a fairly robust base Docker image that has a number of libraries pre-installed to run on the Jetson NX with OpenCV.

The other containers use Alpine Linux to minimize size and resource consumption.

### Topic Naming

Messaging brokers, MQTT included, typically require naming a Topic or queue for messages that are sent/received.  For MQTT, a publisher can push to any Topic and a subscriber can listen to any Topic.  Therefore it is important for an end-to-end system that the various publishers and subscribers in the pipeline are aligned on the structure of the system's Topic tree(s).

I defined a simple single-tier topic on the edge device, called "faces".

On the cloud broker I defined a more distinct topic, called "tst011235".  This was an arbitrary choice during development that allowed me to initially push test messages (without real data) to a public broker (https://www.hivemq.com/public-mqtt-broker/) with some small measure of privacy, assuming few people would be actively monitoring topic tst011235 on the public broker.  I chose to keep this distinct value when converting my code to use my own cloud broker, although I could have also chosen to use "faces".

In other situations I would probably choose a different structure entirely for both the device and cloud topic trees, such as adding sub-categories for different types of events.  For the purpose of this homework these simple choices were adequate.


### Quality of Service (QoS)
The MQTT platform uses quality of service (QoS) to set the send/receive behavior for each message.  It can have 3 levels (basic description):

- 0: Fire-and-forget
- 1: Deliver at-least-once guaranteed
- 2: Deliver one-time-only guaranteed

I chose to use level 1 to most easily test that messages were pushed up the pipeline as they were published on the device.  Level 1 is good for many applications where it is important that messages are sent and received, but it is not important whether they are sent/received multiple times.

I believe that Level 0 would be appropriate for applications where it is useful to record the detection of faces, but where data loss (i.e. dropped messages) is not important.

Level 2 would be appropriate for applications where guarantees that data is not lost are important, for example in security systems where every detected face must be analyzed.


## Implementation

### Setting up the Cloud platform

I setup the cloud platform first.  The address of the instance hosting the message broker is used in the application code on the edge device that pushes messages to the cloud.

First, I setup my local machine to connect to AWS.  This is run from the folder where I store my keyfile.

```
ssh-add -K <keyfilename>.pem
ssh-add -L
```

I then provisioned an instance to host the application containers and connected to it.

```
aws ec2 run-instances --image-id ami-0e76d6dc2679a3ab2 --instance-type t2.micro --security-group-ids sg-0e5d2896cbd248d7a --associate-public-ip-address --key-name w251kp1
```

The public address of this instance is used to configure the forwarding app on the device.  This address can be found by looking on the AWS console or by inspecting the output from a shell command.

```
aws ec2 describe-instances
```

I then connected to the instance.
```
ssh -A ubuntu@<instance address>
```

The instance did not have Docker pre-installed, so I set it up using the standard procedure (https://docs.docker.com/engine/install/ubuntu/).  In the future I would seek an image containing Docker pre-installed or save my own image.

The rest of the commands on the instance were run using sudo.

I cloned the code repository.

```
git clone https://github.com/bjonesneu/w251week3.git
cd w251week3/
```

Created a network bridge.

```
docker network create --driver bridge hw03

```

Built the docker containers.

```
docker build -t mqttbroker -f Dockerfile.mqttbroker .
docker build -t mqttclientcloud -f Dockerfile.mqttclientcloud .
```

MQTT will be configured to listen to port 1883.  We need to setup a special rule on the security group used for launching the instance on AWS to allow public internet traffic on this port. 

After setting up the port listening, I launched the containers:

```
docker run --rm --name mqbroker --network hw03 -p 1883:1883 -d mqttbroker /usr/sbin/mosquitto
docker run --rm --name mqclient --network hw03 -v ~/w251week3:/src -ti mqttclientcloud
```

Then inside the mqclient container:

- Setup AWS credentials inside the mqclient container (using personal credentials).

```
aws configure
```

- Launched the receiver app:

```
python3 /src/cloudreceiverapp.py
```


### Setting up the edge device

The shell commands described in this section may need to be run with sudo.

First, I setup a working directory and cloned the code repository onto the device.  Then all shell commands are run from the code folder.

The working directory was created to map it into the containers.

```
mkdir /usr/app/
cd /usr/app/
git clone https://github.com/bjonesneu/w251week3.git
cd w251week3/
```

Next, I built the Docker containers to run each component.

```
docker build -t mqttbroker -f Dockerfile.mqttbroker .
docker build -t mqttclient -f Dockerfile.mqttclient .
docker build -t opencvclient -f Dockerfile.opencvclient .
```

Before launching the component to forward messages from the device to the cloud, we need to set environment variables using the address and port of the cloud instance running the MQTT broker that was setup above.

```
export CLOUD_MQTT_HOST=<address>
export CLOUD_MQTT_PORT=<port>
```
Usually the port will be set to 1883.

I created 2 shell scripts to automate the launch and shutdown of the device components.  To startup the NX components, run:

```
./nx_launcher.sh
```

The device should now detect faces identified from the camera, create messages, and push them to the cloud.

### Shutting down

After finishing, it is important to shutdown all components on the NX and in the cloud.

For the AWS instance, either:

- Terminate the instance using the AWS console, or
- From a shell on the instance, run:
```
sudo poweroff
```
- From the local terminal session, run:
```
aws ec2  terminate-instances --instance-ids <instance id>
```

<span style='color:red'>It is important to verify that the instance has been terminated.</span>

On the NX, run:

```
./nx_stopper.sh
```

## Closing Thoughts

This solution successfully detected faces on the device, published them through the pipeline and stored them on S3.

Future enhancements I would consider include:

- Passing metadata with detected faces, for example: the detection confidence of the algorithm, the geo-location of the device
- Saving Docker images to Docker Hub for to reduce the need to rebuild images on each platform
- Using Kubernetes as a build manager
- Designing a more sophisticated Topic tree

During development of the cloud solution, I noticed that AWS provides an end-to-end IoT messaging capability, called AWS IoT Core.  This would be something to consider for future versions of this type of solution, where a custom solution may be less desirable, for example in a commercial system.


