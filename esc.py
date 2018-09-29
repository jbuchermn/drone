import RPi.GPIO as GPIO
import time


PWM_FREQ = 50


def duration_to_dc(duration_ms):
    full_ms = 1000./PWM_FREQ
    return 100.*duration_ms/full_ms


class ESC:
    def __init__(self, pin):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        self.pwm = GPIO.PWM(pin, PWM_FREQ)
        self.pwm.start(duration_to_dc(2.01))
        time.sleep(1)
        self.pwm.ChangeDutyCycle(duration_to_dc(0.99))
        time.sleep(1)
        self.set_val(0.)

    def finish(self):
        self.pwm.stop()

    def set_val(self, val):
        self.pwm.ChangeDutyCycle(duration_to_dc(1. + val))


if __name__ == '__main__':
    pin = int(input("PIN? "))
    print("Initializing ESC on PIN %d..." % pin)
    esc = ESC(pin)
    print("...done")

    try:
        while True:
            val = int(input("Value in percent? "))
            esc.set_val(val/100.)
    except KeyboardInterrupt:
        esc.finish()
        GPIO.cleanup()
