import time
import traceback
from threading import Thread
import RPi.GPIO as GPIO

_leds = [24, 23, 22, 27]
_switches = [17, 18]


class LEDState:
    def __init__(self, on=False, blink_interval=0):
        self.on = on
        self.blink_interval = blink_interval
        self.current = 1
        self.current_dur = 0

class SimpleInterface(Thread):
    def __init__(self):
        super().__init__()

        GPIO.setmode(GPIO.BCM)
        for p in _leds:
            GPIO.setup(p, GPIO.OUT)
            GPIO.output(p, 0)
        
        for p in _switches:
            GPIO.setup(p, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self._led_states = [LEDState() for _ in _leds]
        self._switch_pressed = [False for _ in _switches]
        self._switch_callbacks = [lambda: None for _ in _switches]
        self._running = True
        self.start()

    def run(self):
        while self._running:
            for i, p in enumerate(self._led_states):
                if not p.on:
                    GPIO.output(_leds[i], 0)
                elif p.blink_interval > 0:
                    if p.current_dur >= p.blink_interval:
                        p.current = 1 - p.current
                        p.current_dur = 0
                        GPIO.output(_leds[i], p.current)
                    p.current_dur += 1
                else:
                    GPIO.output(_leds[i], 1)

            for i, p in enumerate(self._switch_pressed):
                if self.is_pressed(i) and not p:
                    self._switch_callbacks[i]()

            self._switch_pressed = [self.is_pressed(i) for i in range(len(_switches))]


            time.sleep(.1)

    def close(self):
        self._running = False
        GPIO.cleanup()

    def set_led(self, i, state):
        if self._led_states[i].on == state.on and \
                self._led_states[i].blink_interval == state.blink_interval:
            return
        self._led_states[i] = state

    def on_switch(self, i, func):
        self._switch_callbacks[i] = func

    def is_pressed(self, i):
        return GPIO.input(_switches[i]) == 0


if __name__ == '__main__':
    interf = SimpleInterface()
    interf.on_switch(0, lambda: interf.set_led(0, LEDState(on=True, blink_interval=1)))
    interf.on_switch(1, lambda: interf.set_led(0, LEDState(on=False)))
    try:
        while True:
            time.sleep(1.)

    except Exception as e:
        traceback.print_exc()
    finally:
        interf.close()

