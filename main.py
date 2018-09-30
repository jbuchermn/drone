import RPi.GPIO as GPIO
from esc import ESC
import time

pins = [17, 23, 18, 27]
escs = [ESC("M%d" % (i+1)) for i, pin in enumerate(pins)]

for e, p in zip(escs, pins):
    e.initialize(p)

try:
    for i in range(1000):
        escs[(i+1)%4].set_val(0.1)
        escs[(i+2)%4].set_val(0.1)
        escs[(i+3)%4].set_val(0.1)
        escs[i%4].set_val(0.1)
        print("Thrust on %d" % (i%4))
        for j in range(100):
            escs[i%4].set_val(j/100.)
            time.sleep(0.1)
        for j in range(100):
            escs[i%4].set_val((100.-j)/100.)
            time.sleep(0.1)

except KeyboardInterrupt:
    for e in escs:
        e.finish()

    GPIO.cleanup()
