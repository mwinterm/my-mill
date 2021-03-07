#!/usr/bin/env python
import hal, time
h = hal.component("blink")
h.newpin("in", hal.HAL_BIT, hal.HAL_IN)
h.newpin("out", hal.HAL_BIT, hal.HAL_OUT)
h.ready()
try:
    while 1:
        if h['in']:
          time.sleep(1)
          h['out'] = 1
          time.sleep(1)
          h['out'] = 0
        else:
          h['out'] = 0
except KeyboardInterrupt:
    raise SystemExit