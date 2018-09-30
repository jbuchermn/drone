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
    def __init__(self, name):
        self.name = name

    def initialize(self, pin, calibrate=False):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        self.pwm = GPIO.PWM(pin, PWM_FREQ)

        if calibrate:
            print("Calibrating %s..." % self.name)

            self.pwm.start(signal_to_dc(1.0))
            time.sleep(2)
            self.pwm.ChangeDutyCycle(signal_to_dc(0.0))
            time.sleep(2)

            print("...done")
        else:
            self.pwm.start(signal_to_dc(0.0))

    def finish(self):
        self.pwm.stop()

    def set_val(self, val):
        if val < 0.:
            val = 0.
        if val > 1.:
            val = 1.
        self.pwm.ChangeDutyCycle(signal_to_dc(val))


if __name__ == '__main__':
    pin = int(input("PIN? "))
    esc = ESC("PIN%d" % pin)
    esc.initialize(pin)

    try:
        while True:
            val = int(input("Value in percent? "))
            esc.set_val(val/100.)
    except KeyboardInterrupt:
        esc.finish()
        GPIO.cleanup()
