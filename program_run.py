#!/usr/bin/env python
import hal, time
h = hal.component("program_run")
h.newpin("cycle_button", hal.HAL_BIT, hal.HAL_IN)
h.newpin("pause_button", hal.HAL_BIT, hal.HAL_IN)
h.newpin("is_idle", hal.HAL_BIT, hal.HAL_IN)
h.newpin("is_paused", hal.HAL_BIT, hal.HAL_IN)
h.newpin("is_running", hal.HAL_BIT, hal.HAL_IN)
h.newpin("auto_toggle", hal.HAL_BIT, hal.HAL_IN)
h.newpin("single_toggle", hal.HAL_BIT, hal.HAL_IN)
h.newpin("jog_toggle", hal.HAL_BIT, hal.HAL_IN)
h.newpin("program_mode", hal.HAL_BIT, hal.HAL_IN)
h.newpin("run", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("step", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("resume", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("pause", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("cycle_jog", hal.HAL_BIT, hal.HAL_OUT)
h.ready()


try:
    while 1:
        if (h['cycle_button'] and h['is_idle'] and h['auto_toggle'] and h['program_mode']): #start program
            h['step'] = 0
            h['resume'] = 0
            h['run'] = 1
        elif (h['cycle_button'] and h['single_toggle'] and h['program_mode']): #start program in single step mode
            h['run'] = 0
            h['resume'] = 0
            h['step'] = 1
        elif (h['cycle_button'] and h['is_paused'] and h['auto_toggle'] and h['program_mode']): #restart program after pause
            h['step'] = 0
            h['run'] = 0
            h['resume'] = 1
        elif (not h['is_paused'] and h['single_toggle'] and h['program_mode']): #switch to single step 
            h['step'] = 0
            h['resume'] = 0
            h['run'] = 0
            h['pause'] = 1
        elif (h['pause_button'] and h['program_mode']): #pause program
            h['step'] = 0
            h['resume'] = 0
            h['run'] = 0
            h['pause'] = 1
        elif (h['cycle_button'] and h['is_idle'] and h['jog_toggle'] and h['program_mode']): #start program
            h['step'] = 0
            h['resume'] = 0
            h['run'] = 1
            h['cycle_jog'] = True
        elif (h['cycle_button'] and h['is_paused'] and h['jog_toggle'] and h['program_mode']): #restart program after pause
            h['step'] = 0
            h['run'] = 0
            h['resume'] = 1
            h['cycle_jog'] = True
        elif (h['is_running'] and h['jog_toggle'] and h['program_mode']): #restart program after pause
            h['cycle_jog'] = True
        else:
            h['run'] = 0
            h['step'] = 0
            h['resume'] = 0
            h['pause'] = 0
            h['cycle_jog'] = False
except KeyboardInterrupt:
    raise SystemExit