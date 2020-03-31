# iotDeviceSimulator
Basic Golang CURL client to simulate an Iot camera by polling any youtube livestream and pushing bytes of the livestream to an cloud hosted Enmasse instance's HttP Endpoint. 

The stream can be chosen from any youtube livestream link via an environment variable, since HLS(HTTP live Storage)required access to the index.m3u8 playlist files in order to push the live video segments 

`export STREAMURL=<Desired Stream URL>`

## Prereqs

This module uses the `youtube-dl` library so it must be installed first with the installation instructions from the [following link](https://ytdl-org.github.io/youtube-dl/download.html) 

STILL IN PRODUCTION 
