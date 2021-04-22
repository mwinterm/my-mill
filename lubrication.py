#!/usr/bin/env python
import hal
import time
h = hal.component("lubrication")
h.newparam("lube_command", hal.HAL_BIT, hal.HAL_RW)
h.newpin("lube_pressure", hal.HAL_BIT, hal.HAL_IN)
h.newpin("joint0_integ", hal.HAL_FLOAT, hal.HAL_IN)
h.newpin("joint1_integ", hal.HAL_FLOAT, hal.HAL_IN)
h.newpin("joint2_integ", hal.HAL_FLOAT, hal.HAL_IN)
h.newparam("lube_time", hal.HAL_FLOAT, hal.HAL_RW)
h.newpin("lube_pump", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("integ_reset", hal.HAL_BIT, hal.HAL_OUT)
h.newparam("paused", hal.HAL_BIT, hal.HAL_RW)
h.ready()

h.lube_command = True
start_time = -1.0
lube_timer = time.time()

try:
    while 1:
        h.integ_reset = False

        if h.joint0_integ > 100 or h.joint1_integ > 100 or h.joint2_integ > 100:
            h.lube_command = True

        if time.time() - lube_timer > 180:
            h.lube_command = True

        if h.lube_command:
            h.lube_pump = True

        if h.lube_command and h.lube_pressure and start_time < 0.0:
            start_time = time.time()

        if h.lube_pressure and time.time() - start_time > 15.0:
            print(time.time())
            print(start_time)
            h.lube_command = False
            h.lube_pump = False
            start_time = -1.0
            h.integ_reset = True
            lube_timer = time.time()
        


except KeyboardInterrupt:
    raise SystemExit
