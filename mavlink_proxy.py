import time
from pymavlink import mavutil, mavparm

mavutil.set_dialect("ardupilotmega")

source_system = 255
ip = "/dev/ttyAMA0"
baud = 115200

proxy_ip = "172.16.0.106:14550"


print("Establishing connection...")
connection = mavutil.mavlink_connection(ip,
                                        autoreconnect=True,
                                        source_system=source_system,
                                        baud=baud)
proxy_connection = mavutil.mavlink_connection(proxy_ip,
                                              autoreconnect=True,
                                              source_system=source_system,
                                              baud=baud,
                                              input=False)

while True:
    msg = connection.recv_msg()
    proxy_msg = proxy_connection.recv_msg()
    if msg is not None:
        proxy_connection.write(msg.get_msgbuf())
    if proxy_msg is not None:
        connection.write(proxy_msg.get_msgbuf())


