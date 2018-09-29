from esc import ESC
import time

escs = []
for pin in [18, 23, 17, 27]:
    esc = ESC(pin)
    print("Calibrating %d..." % pin)
    # esc.try_calibrate()
    esc.set_val(0.01)
    escs += [esc]

try:
    for i in range(1000):
        time.sleep(1)
        escs[(i+1)%4].set_val(0.1)
        escs[(i+2)%4].set_val(0.1)
        escs[(i+3)%4].set_val(0.1)
        escs[i%4].set_val(1.0)

except KeyboardInterrupt:
    for e in escs:
        e.finish()

    GPIO.cleanup()
