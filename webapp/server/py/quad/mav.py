import time
import traceback
from threading import Thread
from queue import Queue
from pymavlink import mavutil


"""
Not used at the moment
"""


class MAVLinkConnectionSender(Thread):
    def __init__(self, conn, max_hz):
        super().__init__()
        self._conn = conn
        self._max_hz = max_hz
        self._queue = Queue()
        self._running = True

    def send(self, msg_bytes):
        """
        Send an already packed message
        """
        self._queue.put(msg_bytes)

    def run(self):
        while self._running:
            if self._queue.empty():
                time.sleep(1./self._max_hz)
            else:
                self._conn.write(self._queue.get())

    def close(self):
        self._running = False


class MAVLinkConnectionReceiver(Thread):
    def __init__(self, conn, handler, max_hz):
        super().__init__()
        self._conn = conn
        self._max_hz = max_hz
        self._running = True
        self._handler = handler

    def run(self):
        while self._running:
            msg = self._conn.recv_msg()
            if msg is None:
                time.sleep(1./self._max_hz)
            else:
                self._handler(msg)

    def close(self):
        self._running = False


class MAVLinkConnection:
    def __init__(self, conn, max_hz=100, **kwargs):
        print("Opening MAVLink connection to '%s'..." % conn)
        self._conn = mavutil.mavlink_connection(conn, **kwargs)
        self._send = MAVLinkConnectionSender(self._conn, max_hz)
        self._receive = MAVLinkConnectionReceiver(self._conn,
                                                  self._handle_msg,
                                                  max_hz)

        self._send.start()
        self._receive.start()
        self._on_msg = []

    def on_msg(self, handler):
        self._on_msg += [handler]

    def send(self, msg_bytes):
        self._send.send(msg_bytes)

    def _handle_msg(self, msg):
        if msg.get_type() == "BAD_DATA":
            return

        for handler in self._on_msg:
            handler(msg)

    def close(self):
        self._send.close()
        self._receive.close()


class MAV:
    def __init__(self, conn="/dev/ttyAMA0", baud=115200):
        self._baud = baud
        self._master = MAVLinkConnection(
            conn,
            baud=self._baud,
            autoreconnect=True,
            source_system=255)

        self._on_msg = []
        self._master.on_msg(self._handle_msg)

        self._proxy = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        self.close()

    def close(self):
        self._master.close()
        if self._proxy is not None:
            self._proxy.close()

    def set_proxy(self, conn):
        if self._proxy is not None:
            self._proxy.close()

        self._proxy = MAVLinkConnection(
            conn,
            baud=self._baud,
            autoreconnect=True,
            source_system=255,
            input=False)
        self._proxy.on_msg(self._handle_proxy_msg)

    def on_msg(self, handler):
        self._on_msg += [handler]

    def _handle_msg(self, msg):
        if self._proxy is not None:
            self._proxy.send(msg.get_msgbuf())

        for handler in self._on_msg:
            handler(msg)

    def _handle_proxy_msg(self, msg):
        self._master.send(msg.get_msgbuf())



if __name__ == '__main__':
    with MAV() as mav:
        mav.set_proxy("172.16.0.106:14550")
        while True:
            time.sleep(1)

