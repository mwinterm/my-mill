#!/usr/bin/env python
import hal
import time

h = hal.component("geared_spindle")

#in-pins
h.newpin("cw", hal.HAL_BIT, hal.HAL_IN)
h.newpin("ccw", hal.HAL_BIT, hal.HAL_IN)
h.newpin("on", hal.HAL_BIT, hal.HAL_IN)
# h.newpin("toolchange_button", hal.HAL_BIT, hal.HAL_IN)
h.newpin("estop_active", hal.HAL_BIT, hal.HAL_IN)
# h.newpin("e_stop_contactor", hal.HAL_BIT, hal.HAL_IN)
# h.newpin("feed_contactor", hal.HAL_BIT, hal.HAL_IN)
# h.newpin("halui_mode_is_manual", hal.HAL_BIT, hal.HAL_IN)
# h.newpin("rpm_surveillance", hal.HAL_BIT, hal.HAL_IN)
# h.newpin("vel_xyz", hal.HAL_FLOAT, hal.HAL_IN)

#out-pins
# h.newpin("machine_on", hal.HAL_BIT, hal.HAL_OUT)
# h.newpin("prepare_toolchange", hal.HAL_BIT, hal.HAL_OUT)
# h.newpin("toolchange_button_led", hal.HAL_BIT, hal.HAL_OUT)
# h.newpin("axis_1_approve", hal.HAL_BIT, hal.HAL_OUT)
# h.newpin("axis_2_approve", hal.HAL_BIT, hal.HAL_OUT)
# h.newpin("axis_3_approve", hal.HAL_BIT, hal.HAL_OUT)
# h.newpin("feed_driver", hal.HAL_BIT, hal.HAL_OUT)
# h.newpin("unclamp_3rd_axis", hal.HAL_BIT, hal.HAL_OUT)
# h.newpin("toolchange_button_out", hal.HAL_BIT, hal.HAL_OUT)

h.newparam("rpms", hal.HAL_S32, hal.HAL_RW)
# h.newparam("tc_button_old", hal.HAL_BIT, hal.HAL_RW)
# h.newparam("drives_active", hal.HAL_BIT, hal.HAL_RW)
h.newparam("debug", hal.HAL_S32, hal.HAL_RW)

h.ready()

try:
    while True:
        if h.estop_active:
            h.debug = 1
            #action when estop occurs
        else:
            h.debug = 2            

except KeyboardInterrupt:
    raise SystemExit
