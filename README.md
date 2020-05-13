# 2020Summit-IoT-Streaming-Demo
Live Streaming and Analytics Demo for 2020 Virtual Summit 

It is split up into three major pieces 

- `IoT Camera Simulator` -> Pulls video from any youtube livestream and pushes it to the Kafka http bridge 

- `Analytics Service` -> Gets live video data from kafka in the form of a Cloud Event, Sends the data to tensorflow-serving for inference, overlays the inference on the video, and uploads live video segments to ceph object storage 

- `Video Serving Service` -> Pulls the live video stream segments from ceph, builds the HLS playlist file, serves the inferenced video to the user with a static flask based webapp

The overall system diagram and main components are shown below

![Demo Overview](https://raw.githubusercontent.com/redhat-iot/2020Summit-IoT-Streaming-Demo/master/Docs/overall_arch.png)

# Deploy this demo yourself 

This POC demo uses some great cloud-native technologies, follow the instructions to spin it up on a personal cluster It can be deployed with the manual instuctions shown below or the Simple IoTCLI instuctions if using the [IoTCLI command line tool](https://github.com/redhat-iot/iot-dev)

## IoTCLI Install

### Prerequisites For IoTCLI Install 

1. An Openshift Cluster 4.1> 
- For a quickstart [Code ready containers](https://developers.redhat.com/products/codeready-containers/overview) may be used however they have not been tested with this system. 

2. The latest IoTCLI download moved into yout `$PATH`

### Provision Knative 

1. Run `IoTCLI knative setup` which will setup knative eventing and serving on your cluster 

2. Check status with `IoTCLI knative setup --status` Which should resemble the following 

```
2020/04/24 15:14:00 knative Serving Install Status:
DependenciesInstalled==True
DeploymentsAvaliable==True
InstallSucceeded=True
Ready=True
2020/04/24 15:14:00 Context switched to namespace: knative-eventing
2020/04/24 15:14:00 NAME                                   READY   STATUS    RESTARTS   AGE
broker-controller-58fbf6569b-zgmz8     1/1     Running   0          12m
eventing-controller-5b9c5765dd-2w7cf   1/1     Running   2          12m
eventing-webhook-5cd6c688f4-7qzxw      1/1     Running   0          12m
imc-controller-845fc8776b-rcpzf        1/1     Running   0          12m
imc-dispatcher-5f9565cdbd-rmwlr        1/1     Running   0          12m
```

### Provision Kafka 

1. Run `IoTCLI kafka setup` to deploy kafka to your cluster with the strimzi Operator 

2. Deploy the http->kafka bridge with `IoTCLI kafka bridge` 

3. Follow the Instructions to check status 
- `To check status of Kafka HTTP bridge run 'curl -v GET http://my-bridge.io/healthy'`

  Which should show 

  ```
  < HTTP/1.1 200 OK
  < content-length: 0
  * Added cookie 9d04d3bd5bc37b277b860a02c6cf350d="69a5f362b53812ea1dbbee66d616958b" for domain my-bridge.io, path /, expire 0
  < Set-Cookie: 9d04d3bd5bc37b277b860a02c6cf350d=69a5f362b53812ea1dbbee66d616958b; path=/; HttpOnly
  < Cache-control: private
  < 
  * Connection #1 to host my-bridge.io left intact
  ```

### Setup Ceph Object Storage 

1. Run `IoTCLI ceph setup` to provision ceph 
- This will tak some time for all the resources to become available 

2.Run `IoTCLI ceph user <ceph username` to setup a new ceph user connected to credential store `my-store`

3.Run `IoTCLI ceph secrets <ceph username>` to get the login secrets for your ceph instance and the endpoint name, these will be used later. 

### Setup the Tensorflow Serving Deployments 

1. Run `IoTCLI tensorflowServing setup` Which will spin up the tensorflow serving pod 

### Deploy the `Video Analytics` knative service 

1. Run 

```
IoTCLI knative service video-analytics -n kafka --cephEndpoint <Your Ceph Endpoint> --cephAccessKey <Your Ceph Access Key> --cephSecretKey<Your Ceph Secret Key>
```

### Setup the Kafka -> Knative Bridge 

1. Run 
```
IoTCLI knative source kafka video-analytics -n kafka 
```

### Start the IoT Video Simulator

1. Navigate to the `iotDeviceSimulator-kafka` with 
-  `cd iotDeviceSimulator-kafka`
2. Set the `STREAMURL` environment variable with 
- `export STREAMURL=<Desired Youtube livestream>`
3. Set Kafka Bridge Endpoint for this demo as follows 
- `export ENDPOINT=my-bridge.io/topics/my-topic`
4. Start the Simulator
- `go run ./cmd` 

### Deploy the `video-serving` service

1. Run 
```
IoTCLI service video-serving -n kafka --cephEndpoint <Your Ceph Endpoint> --cephAccessKey <Your Ceph Access Key> --cephSecretKey<Your Ceph Secret Key>` 
```
to deploy the service 

2. Run `IoTCLI service --status` to get the url for the `video serving` service 

```
NAME            URL                                                           LATESTCREATED         LATESTREADY           READY   REASON
video-analytics   http://video-analytics.kafka.apps.astoycos-ocp.shiftstack.com   video-analytics-895k8   video-analytics-895k8   True 
video-serving   http://video-serving.kafka.apps.astoycos-ocp.shiftstack.com   video-serving-9cfps   video-serving-9cfps   True   
```

3. Follow the [final step instructions](#Final-Steps)



## Manual Install from Source 

### Prerequisites For Manual Install from Source

1. An Openshift Cluster 4.1> 
- For a quickstart [Code ready containers](https://developers.redhat.com/products/codeready-containers/overview) may be used however they have not been tested with this system. 

2. Knative Eventing and Serving installed 
- Knative Operator [install instructions](https://docs.openshift.com/container-platform/4.3/serverless/installing_serverless/installing-openshift-serverless.html) 
- Knative Serving [install instructions](https://docs.openshift.com/container-platform/4.3/serverless/installing_serverless/installing-knative-serving.html)
- Knative Eventing [install instructions](https://knative.dev/docs/eventing/getting-started/#installing-knative-eventing)

### Setup Kafka with some custom modules 

1. Create a namespace for the Apache Kafka installation 
-  `oc create namespace kafka `

2. Install the Strimzi operator 
-  `curl -L "https://github.com/strimzi/strimzi-kafka-operator/releases/download/0.16.2/strimzi-cluster-operator-0.16.2.yaml" \
  | sed 's/namespace: .*/namespace: kafka/' \
  | kubectl -n kafka apply -f -`

3. Configure the Kafka Cluster, with custom `max.message.bytes parameter` 
- ` oc apply -n kafka -f demo_yamls/kafka.yaml`

4. [Setup HTTP-Kafka Bridge](https://strimzi.io/2019/11/05/exposing-http-bridge.html) 
- `oc apply -n kafka apply -f demo_yamls/kafka-bridge.yaml` 
- Create a K8's Ingress Resource to access bridge from outside cluster
    - `kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/nginx-0.30.0/deploy/static/mandatory.yaml`
    - `kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/nginx-0.30.0/deploy/static/provider/cloud-generic.yaml`
    - `oc apply -f demo/yamls/ingress.yaml`

5. Run `curl -v GET http://my-bridge.io/healthy` to check bridge, output should be as follows: 
```
> GET /healthy HTTP/1.1
> Host: my-bridge.io:80
> User-Agent: curl/7.61.1
> Accept: */*
> 
< HTTP/1.1 200 OK
< content-length: 0
```

### Setup Rook and Ceph Object storage 

Follow Open Data Hub's instructions for [Ceph installation with the Rook operator](https://opendatahub.io/docs/administration/advanced-installation/object-storage.html)

And make sure to save the resulting s3 credentials 

### Deploy Tensorflow Serving

Do to the video inference the demo using a tensorflow-serving container with a pre-trained object detction model from the [Model zoo library](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md) specifially using the [ssd_inception_v2_cocossd_inception_v2_coco Model](http://download.tensorflow.org/models/object_detection/ssd_inception_v2_coco_2018_01_28.tar.gz) 

1. To deploy this model simply run 
- `oc apply -n kafka -f demo_yamls/tensorflow-deployment.yaml`
```
[astoycos@localhost 2020Summit-IoT-Streaming-Demo]$ oc get pods --selector=app=coco-server
NAME                                    READY   STATUS    RESTARTS   AGE
tensorflow-deployment-9d867d795-5q4kb   1/1     Running   0          2d4h
```

2. To Ensure the Serving pod is up run 
- `oc get pods --selector=app=coco-server` It should show the following 


3. To get the podIP that will be used by the Knative Video Service Run: 
- `export IP=$(oc get pods --selector=app=coco-server -o jsonpath='{.items[*].status.podIP'})`

### Deploy Knative Video Service  

1. Apply your S3 Credentials and endpoint in `demo_yamls/video-service.yaml.in` 

2. Apply the knative service with the environment configs run 

`cat demo_yamls/video-service.yaml.in | envsubst | oc apply -n kafka -f -`

3. Make sure the knative service is ready with 

`oc get ksvc` Which should resemble the following 

```
NAME            URL                                                           LATESTCREATED         LATESTREADY           READY   REASON
video-service   http://video-service.kafka.apps.astoycos-ocp.shiftstack.com   video-service-895k8   video-service-895k8   True    
```
4. Deploy the Kafka-> Knative Source with 

`oc apply -n kafka -f demo_yamls/kafka-event-source.yaml`

Now the Analyzed video stream segments should be stored in Ceph

### Start the IoT camera simulator 

1. Navigate to the `iotDeviceSimulator-kafka` with 
-  `cd iotDeviceSimulator-kafka`
2. Set the `STREAMURL` environment variable with 
- `export STREAMURL=<Desired Youtube livestream>`
3. Set Kafka Bridge Endpoint for this demo as follows 
- `export ENDPOINT=my-bridge.io/topics/my-topic`
4. Start the Simulator
- `go run ./cmd` 

### Deploy Knative Serving Service 

1. Apply your S3 Credentials and endpoint in `demo_yamls/video-serving-service.yaml` 

2. Apply the service with 

`oc apply -n kafka demo_yamls/video-serving-service.yaml`

3. Get the service URL with 

`oc get ksvc` 

```
NAME            URL                                                           LATESTCREATED         LATESTREADY           READY   REASON
video-serving   http://video-serving.kafka.apps.astoycos-ocp.shiftstack.com   video-serving-jsct5   video-serving-jsct5   True    
```

Move to [Final Step instructions](Final-Steps)

## Final Steps

Go to the a web browser and type in the `video-serving` service's URL. Add `/video/out.m3u8` to the path for a final URL as follows 

`http://video-serving.kafka.apps.astoycos-ocp.shiftstack.com/video/out.m3u8`

The following webpage will resemble the following, showing live video streaming an anlytics

![app image](https://raw.githubusercontent.com/redhat-iot/2020Summit-IoT-Streaming-Demo/master/Docs/Screenshot%20from%202020-04-01%2017-16-27.png)

Note:: You may need to add the service's URL to your `etc/hosts` file for correct DNS lookup 
