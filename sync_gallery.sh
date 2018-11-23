#!/bin/bash
shopt -s nullglob

# Mount
mkdir /mnt/sdcard
mount /dev/mmcblk0p1 /mnt/sdcard

# Convert
for f in /mnt/sdcard/home/pi/Camera/vid/*.avi; do
    ffmpeg -i $f -vf "transpose=1,transpose=1" ${f%.avi}.mp4
    rm $f
done

# Sync
mkdir -p Camera/vid
mkdir -p Camera/img
rsync -av /mnt/sdcard/home/pi/Camera/img ./Camera
rsync -av /mnt/sdcard/home/pi/Camera/vid ./Camera

# Cleanup
umount /dev/mmcblk0p1
rm -rf /mnt/sdcard
