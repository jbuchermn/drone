import time
import RPi.GPIO as GPIO

_leds = [24, 23, 22, 27]
_switches = [17, 18]

class SimpleInterface:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        for p in _leds:
            GPIO.setup(p, GPIO.OUT)
            GPIO.output(p, 0)
        
        for p in _switches:
            GPIO.setup(p, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def close(self):
        GPIO.cleanup()

    def set_led(self, i, state):
        GPIO.output(_leds[i], state)


if __name__ == '__main__':
    interf = SimpleInterface()
    try:
        while True:
            interf.set_led(0, GPIO.input(_switches[0]))
            interf.set_led(1, GPIO.input(_switches[1]))
            time.sleep(0.1)

    except Exception as e:
        print(e)
    finally:
        interf.close()

