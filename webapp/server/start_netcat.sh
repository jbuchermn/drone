#!/bin/sh
raspivid -n -ih -t 0 -rot 0 -w 1280 -h 720 -fps 30 -b 2000000 -o - | nc -lkv4 5001
