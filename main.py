import RPi.GPIO as GPIO
from esc import ESC
import time

pins = [18, 23, 17, 27]
escs = [ESC(pin) for pin in pins]

try:
    for i in range(1000):
        time.sleep(1)
        print("Thrust on %d" % (i%4))
        escs[(i+1)%4].set_val(0.1)
        escs[(i+2)%4].set_val(0.1)
        escs[(i+3)%4].set_val(0.1)
        escs[i%4].set_val(0.9)

except KeyboardInterrupt:
    for e in escs:
        e.finish()

    GPIO.cleanup()
