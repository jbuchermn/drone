#!/bin/sh
name=$(date --iso-8601=seconds)
mkdir -p Camera/fpv_vid
vlc v4l2:///dev/video2 ":sout=#duplicate{dst=display,dst=std{access=file,mux=avi,dst='./Camera/fpv_vid/$name.avi'}}"

ffmpeg -y -i ./Camera/fpv_vid/$name.avi ./Camera/fpv_vid/$name.mp4
rm ./Camera/fpv_vid/$name.avi
