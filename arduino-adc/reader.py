import serial
import struct

class ADC():
    def __init__(self):
        self._data = (0, 0, 0)
        self._running = True

    def get_data(self):
        return self._data

with serial.Serial("/dev/ttyUSB0", 19200) as ser:
    while True:
        if ser.read()== b'\xff':
            buf = ser.read(3*2)
            x = struct.unpack('hhh', buf)
            print(",".join(map(str, x)))
