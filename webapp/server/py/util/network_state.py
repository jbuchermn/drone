from enum import Enum
from subprocess import Popen, PIPE

class NetworkState(Enum):
    HOTSPOT = 1,
    CLIENT = 2,
    ERROR = 15


def get_network_state():
    p = Popen("wpa_cli -i wlan0 status".split(" "), stdout=PIPE, stderr=PIPE)
    stdout, _ = p.communicate()
    stdout = stdout.decode("utf-8")

    ip = None
    ssid = None
    for l in stdout.split("\n"):
        if l.strip().startswith("ip_address"):
            ip = l.split("=")[1]
        elif l.strip().startswith("ssid"):
            ssid = l.split("=")[1]

    if ip is not None and ssid is not None:
        return NetworkState.CLIENT


    p = Popen("ifconfig".split(" "), stdout=PIPE, stderr=PIPE)
    stdout, _ = p.communicate()
    stdout = stdout.decode("utf-8")

    found_10005 = False
    found_BROADCAST = False

    for l in stdout.split("\n"):
        if "10.0.0.5" in l:
            found_10005 = True
        if "BROADCAST" in l:
            found_BROADCAST = True

    if found_10005 and found_BROADCAST:
        return NetworkState.HOTSPOT

    return NetworkState.ERROR
