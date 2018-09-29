import RPi.GPIO as GPIO
import time


PWM_FREQ = 1000


def duration_to_dc(duration_ms):
    full_ms = 1000./PWM_FREQ
    return 100.*duration_ms/full_ms


class ESC:
    def __init__(self, pin, start_val=0.):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.out)
        self.pwm = GPIO.PWM(pin, PWM_FREQ)
        self.pwm.start(duration_to_dc(1. + start_val))

    def finish(self):
        self.pwm.stop()

    def try_calibrate(self):
        self.set_val(1.)
        time.sleep(5)
        self.set_val(0.)
        time.sleep(5)

    def set_val(self, val):
        self.pwm.ChangeDutyCycle(duration_to_dc(1. + val))


if __name__ == '__main__':
    pin = int(input("PIN? "))
    print("Initializing ESC on PIN %d" % pin)
    esc = ESC(pin)
    print("Trying to calibrate...")
    esc.try_calibrate()
    print("...done")

    while True:
        val = int(input("Value in percent? "))
        esc.set_val(val/100.)
