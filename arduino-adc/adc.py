import serial
import struct
import threading

class ADC():
    def __init__(self, size=3, interval=0.01, baud=19200,
            interface="/dev/ttyUSB0"):
        self._data = (0,)*size
        self._size = size
        self._interval = interval
        self._baud = baud
        self._interface = interface
        self._running = True
        # self._serial = None
        self._serial = serial.Serial(interface, baud)
        self._timer = threading.Timer(self._interval, self.read)
        self._timer.start()

    def get_data(self):
        return self._data

    def stop(self):
        self._timer.cancel()
        self._running = False

    def read(self):
        self._timer = threading.Timer(self._interval, self.read)
        self._timer.start()
        if not self._serial:
            import random
            self._data = (random.random(), )
            return
        while self._serial.read() != b'\xff':
            pass
        buf = self._serial.read(self._size*2)
        x = struct.unpack('h'*self._size, buf)
        self._data = x

