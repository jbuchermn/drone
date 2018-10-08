#!/bin/sh
raspivid -fps 25 -h 720 -w 1080 -n -t 0 -b 2000000 -o - | gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=172.16.0.110 port=5000
