#!/bin/sh
nc 172.16.0.105 5001 | mplayer -fps 30 -demuxer h264es -
