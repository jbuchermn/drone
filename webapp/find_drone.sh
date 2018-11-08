#!/bin/sh

# Set WIFI_CONNECTION to the SSID the drone would automatically connect with

DRONE_IP="172.16.0.127"
DRONE_FOUND=0

nmcli connection up id $WIFI_CONNECTION

echo "Looking in $WIFI_CONNECTION..."
if ping -c 1 $DRONE_IP > /dev/null 2>&1; then
    echo "...yes"
    DRONE_FOUND=1
else
    echo "...no"
    nmcli connection down id $WIFI_CONNECTION

    echo "Looking for hotspot..."
    nmcli dev wifi rescan > /dev/null 2>&1
    if nmcli dev wifi list | grep -q raspberry-drone; then
        echo "...yes"
        nmcli dev wifi connect raspberry-drone password "1234567890"
        DRONE_IP="10.0.0.5"

        if ping -c 1 $DRONE_IP > /dev/null 2>&1; then
            DRONE_FOUND=1
        fi
    else
        echo "...no"
    fi
   if [ "$DRONE_FOUND" = 0 ]; then     
        nmcli connection up id $WIFI_CONNECTION
    fi
fi

if [ "$DRONE_FOUND" = 1 ]; then
    echo "Found drone @ IP: $DRONE_IP"
    read -p "Command ([s]sh, [f]irefox) " command
    if [ $command = s ]; then
        ssh "pi@$DRONE_IP"
    fi
    if [ $command = f ]; then
        firefox "http://$DRONE_IP:5000" &
    fi
else
    echo "Could not find drone"
fi
