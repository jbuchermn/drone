import RPi.GPIO as GPIO
import time


PWM_FREQ = 100
MIN_WIDTH_US = 1064
MAX_WIDTH_US = 1864


def signal_to_dc(signal):
    duration_us = MIN_WIDTH_US + signal*(MAX_WIDTH_US - MIN_WIDTH_US)
    full_us = 1000000./PWM_FREQ
    return 100.*duration_us/full_us


class ESC:
    def __init__(self, name, pin):
        self.name = name
        self.pin = pin
        self._pwm = None

    def _initialize(self):
        GPIO.setup(self.pin, GPIO.OUT)
        self._pwm = GPIO.PWM(self.pin, PWM_FREQ)

    def finish(self):
        self._pwm.stop()

    def set_val(self, val):
        if val < 0.:
            val = 0.
        if val > 1.:
            val = 1.
        self._pwm.ChangeDutyCycle(signal_to_dc(val))


class ESCs:
    def __init__(self):
        self.escs = []

    def add(self, name, pin):
        self.escs += [ESC(name, pin)]

    def initialize(self, calibrate=False):
        GPIO.setmode(GPIO.BCM)
        for e in self.escs:
            e._initialize()

        if calibrate:
            print("Calibrating ESCs...")
            for e in self.escs:
                e._pwm.start(signal_to_dc(1.0))

            time.sleep(2.5)

            for e in self.escs:
                e._pwm.ChangeDutyCycle(signal_to_dc(0.0))

            time.sleep(2.5)

        else:
            for e in self.escs:
                e._pwm.start(signal_to_dc(0.0))

    def finish(self):
        for e in self.escs:
            e.finish()


if __name__ == '__main__':
    pins = input("PIN? ").split(",")
    pins = [int(pin) for pin in pins]

    escs = ESCs()
    for pin in pins:
        escs.add("PIN%d" % pin, pin)

    escs.initialize(calibrate=True)

    try:
        while True:
            val = int(input("Value in percent? "))
            for e in escs.escs:
                e.set_val(val/100.)
    finally:
        escs.finish()
        GPIO.cleanup()
