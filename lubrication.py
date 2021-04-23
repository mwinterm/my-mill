#!/usr/bin/env python
import hal
import time
h = hal.component("lubrication")
h.newparam("lub_command", hal.HAL_BIT, hal.HAL_RW)
h.newparam("lub_cycle_time", hal.HAL_FLOAT, hal.HAL_RW)
h.newparam("paused", hal.HAL_BIT, hal.HAL_RW)
h.newparam("lub_interval_time", hal.HAL_FLOAT, hal.HAL_RW)
h.newparam("lub_interval_timer", hal.HAL_FLOAT, hal.HAL_RO)
h.newparam("joint0_lub_dist", hal.HAL_FLOAT, hal.HAL_RW)
h.newparam("joint1_lub_dist", hal.HAL_FLOAT, hal.HAL_RW)
h.newparam("joint2_lub_dist", hal.HAL_FLOAT, hal.HAL_RW)
h.newparam("joint0_lub_hubs", hal.HAL_FLOAT, hal.HAL_RW)
h.newparam("joint1_lub_hubs", hal.HAL_FLOAT, hal.HAL_RW)
h.newparam("joint2_lub_hubs", hal.HAL_FLOAT, hal.HAL_RW)
h.newpin("lub_pressure", hal.HAL_BIT, hal.HAL_IN)
h.newpin("joint0_integ", hal.HAL_FLOAT, hal.HAL_IN)
h.newpin("joint1_integ", hal.HAL_FLOAT, hal.HAL_IN)
h.newpin("joint2_integ", hal.HAL_FLOAT, hal.HAL_IN)
h.newpin("joint0_vel", hal.HAL_FLOAT, hal.HAL_IN)
h.newpin("joint1_vel", hal.HAL_FLOAT, hal.HAL_IN)
h.newpin("joint2_vel", hal.HAL_FLOAT, hal.HAL_IN)
h.newpin("lub_pump", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("integ_reset", hal.HAL_BIT, hal.HAL_OUT)


h.ready()

h.lub_command = True
start_time = -1.0
lub_timer = time.time()

try:
    while 1:
        h.integ_reset = False
        h.lub_interval_timer = time.time() - lub_timer

        if h.joint0_integ > h.joint0_lub_dist or h.joint1_integ > h.joint1_lub_dist or h.joint2_integ > h.joint2_lub_dist:
            h.lub_command = True

        if time.time() - lub_timer > h.lub_interval_time:
            h.lub_command = True

        if h.lub_command:
            h.lub_pump = True

        if h.lub_command and h.lub_pressure and start_time < 0.0:
            start_time = time.time()

        if h.lub_pressure and time.time() - start_time > h.lub_cycle_time:
            print(time.time())
            print(start_time)
            h.lub_command = False
            h.lub_pump = False
            start_time = -1.0
            h.integ_reset = True
            lub_timer = time.time()
        


except KeyboardInterrupt:
    raise SystemExit
