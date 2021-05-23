#!/usr/bin/env python
import hal
import time
import linuxcnc
from linuxcnc_timer import Timer
from debug import Debug


c = linuxcnc.command()

# c.error_msg('Error')
# c.text_msg('Text')
# c.display_msg('Display')

h = hal.component("lubrication")
h.newparam("lub_command", hal.HAL_BIT, hal.HAL_RW)
h.newparam("lub_cycle_time", hal.HAL_FLOAT, hal.HAL_RW)
h.newparam("num_cycles", hal.HAL_S32, hal.HAL_RW)
h.newparam("start_cycles_pause", hal.HAL_FLOAT, hal.HAL_RW)
h.newparam("paused", hal.HAL_BIT, hal.HAL_RW)
h.newparam("lub_warning_interval", hal.HAL_FLOAT, hal.HAL_RW)
h.newparam("lub_interval_time", hal.HAL_FLOAT, hal.HAL_RW)
h.newparam("lub_interval_timer", hal.HAL_FLOAT, hal.HAL_RO)
h.newparam("joint0_lub_dist", hal.HAL_FLOAT, hal.HAL_RW)
h.newparam("joint1_lub_dist", hal.HAL_FLOAT, hal.HAL_RW)
h.newparam("joint2_lub_dist", hal.HAL_FLOAT, hal.HAL_RW)
h.newparam("joint0_lub_hubs", hal.HAL_FLOAT, hal.HAL_RW)
h.newparam("joint1_lub_hubs", hal.HAL_FLOAT, hal.HAL_RW)
h.newparam("joint2_lub_hubs", hal.HAL_FLOAT, hal.HAL_RW)

h.newpin("machine_is_on", hal.HAL_BIT, hal.HAL_IN)
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

while not h.machine_is_on:
    time.sleep(0.1)


#initialize
first = True
num_cycles_start = 0
pressure_time = -1.0
lub_timer = time.time() #timer for periodic time-based lubrication
paused_timer = -1.0 #is set when a pause command is issued

joint0_vel_old = 1.0
joint1_vel_old = 1.0
joint2_vel_old = 1.0
joint0_hubs = 0
joint1_hubs = 0
joint2_hubs = 0



lub_cycle_timer = Timer(h.lub_cycle_time)
lub_debug = Debug("lubrication debug")
lub_debug.level = 100

try:
    while 1:
        lub_debug.msg()
        if not h.machine_is_on:
            
            if first:
                lub_debug.level = 1
                lub_debug.msg()
                # has to be set here as ini variables might not be read yet earlier on
                num_cycles_start = h.num_cycles
            else: 
                lub_debug.level = 2
                lub_debug.msg()
                h.num_cycles = num_cycles_start

            pressure_time = -1.0
            lub_timer = time.time() #timer for periodic time-based lubrication
            paused_timer = -1.0 #is set when a pause command is issued

            joint0_vel_old = 1.0
            joint1_vel_old = 1.0
            joint2_vel_old = 1.0
            joint0_hubs = 0
            joint1_hubs = 0
            joint2_hubs = 0
        else:
            lub_debug.level = 3
            lub_debug.msg()
            first = False #mark that it is not the first run ever

            h.integ_reset = False
            h.lub_interval_timer = time.time() - lub_timer

            #do initial lubrications at startup or after estop
            if h.num_cycles < 0:
                lub_debug.level = 4
                lub_debug.msg()
                h.lub_command = True

            #do distance traveled based lubrication
            if h.joint0_integ > h.joint0_lub_dist or h.joint1_integ > h.joint1_lub_dist or h.joint2_integ > h.joint2_lub_dist:
                h.lub_command = True

            #count direction changes per axis
            if h.joint0_vel*joint0_vel_old < 0:
                joint0_vel_old = h.joint0_vel
                joint0_hubs += 1

            if h.joint1_vel*joint1_vel_old < 0:
                joint1_vel_old = h.joint1_vel
                joint1_hubs += 1

            if h.joint2_vel*joint2_vel_old < 0:
                joint2_vel_old = h.joint2_vel
                joint2_hubs += 1

            #do hubs based lubrication
            if joint0_hubs > h.joint0_lub_hubs or joint1_hubs > h.joint1_lub_hubs or joint2_hubs > h.joint2_lub_hubs:
                h.lub_command = True

            #do time based lubrication
            if time.time() - lub_timer > h.lub_interval_time:
                h.lub_command = True

            #execute lubrication
            if h.lub_command & h.paused:
                lub_debug.level = 5
                lub_debug.msg()
                h.lub_pump = False
                if paused_timer < 0:
                    paused_timer = time.time()
                elif time.time() - paused_timer > h.lub_warning_interval:
                    print("Warning: Lubrication is paused")
                    c.text_msg("Warning: Lubrication is paused")
                    paused_timer = time.time()
            elif h.lub_command: 
                lub_debug.level = 6
                lub_debug.msg()
                h.lub_pump = True
                pressure_delay_time = time.time()

            #check if it takes too long to build pressure
            if h.lub_command and (not h.lub_pressure) and (time.time() - pressure_delay_time > 3.0):
                lub_debug.level = 7
                lub_debug.msg()
                c.error_msg("Lubrication not working, no pressure building up.")
                pressure_delay_time = time.time() + 30.0

            #start the timer for lubrication based on pressure
            if h.lub_command and h.lub_pressure:
                lub_debug.level = 8
                lub_debug.msg()
                lub_cycle_timer.start()

            #end the lub cycle
            if h.lub_pressure and h.lub_command and not lub_cycle_timer():
                lub_debug.level = 9
                lub_debug.msg()
                h.lub_command = False
                h.lub_pump = False
                h.integ_reset = True
                lub_timer = time.time()
                h.num_cycles +=1
                paused_timer = -1.0
                joint0_hubs = 0
                joint1_hubs = 0
                joint2_hubs = 0

except KeyboardInterrupt:
    raise SystemExit
