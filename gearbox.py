#!/usr/bin/env python
import hal
import time
import linuxcnc
from linuxcnc_timer import Timer
from debug import Debug


c = linuxcnc.command()


h = hal.component("gearbox")
h.newpin("estop", hal.HAL_BIT, hal.HAL_IN)

h.newpin("spindle_on", hal.HAL_BIT, hal.HAL_IN)
h.newpin("forward", hal.HAL_BIT, hal.HAL_IN)
h.newpin("reverse", hal.HAL_BIT, hal.HAL_IN)
h.newpin("rpm_surveillance", hal.HAL_BIT, hal.HAL_IN)
h.newpin("spindle_contactor", hal.HAL_BIT, hal.HAL_IN)

h.newpin("spindle_motor", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("soft_start", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("cw", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("ccw", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("stage_1", hal.HAL_BIT, hal.HAL_IN)
h.newpin("stage_2", hal.HAL_BIT, hal.HAL_IN)
h.newpin("spindle_break", hal.HAL_BIT, hal.HAL_OUT)

h.newparam("block_1_cmd", hal.HAL_S32, hal.HAL_RW)
h.newparam("block_2_cmd", hal.HAL_S32, hal.HAL_RW)
h.newparam("block_3_cmd", hal.HAL_S32, hal.HAL_RW)
h.newparam("block_1_pos", hal.HAL_S32, hal.HAL_RO)
h.newparam("block_2_pos", hal.HAL_S32, hal.HAL_RO)
h.newparam("block_3_pos", hal.HAL_S32, hal.HAL_RO)
h.newparam("block_1_set", hal.HAL_BIT, hal.HAL_RO)
h.newparam("block_2_set", hal.HAL_BIT, hal.HAL_RO)
h.newparam("block_3_set", hal.HAL_BIT, hal.HAL_RO)
h.newpin("block_1_1", hal.HAL_BIT, hal.HAL_IN)
h.newpin("block_1_2", hal.HAL_BIT, hal.HAL_IN)
h.newpin("block_2_1", hal.HAL_BIT, hal.HAL_IN)
h.newpin("block_2_2", hal.HAL_BIT, hal.HAL_IN)
h.newpin("block_3_1", hal.HAL_BIT, hal.HAL_IN)
h.newpin("block_3_2", hal.HAL_BIT, hal.HAL_IN)
h.newpin("current_measurement", hal.HAL_BIT, hal.HAL_IN)

h.newpin("block_1_forward", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("block_1_backward", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("block_2_forward", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("block_2_backward", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("block_3_forward", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("block_3_backward", hal.HAL_BIT, hal.HAL_OUT)

h.ready()


soft_start_timer = Timer(3.0)
start_check_timer = Timer(0.5)
current_timer = Timer(1.0)
#block_reset_timer = Timer(0.15)
block_reset_timer = Timer(0.5)
# block_spindle_timer = Timer(0.2)
block_spindle_timer = Timer(2.0)

current_alarm_type = ""
spindle_on = False

block_1_set = True
block_2_set = True
bolck_3_set = True
block_1_pos = 0
block_2_pos = 0
block_3_pos = 0
block_pos = 0
block_cmd = 0
b_ = ''
b_1 = ''
b_2 = ''



#just for initialization
block_forward = h.block_1_forward 
block_backward = h.block_1_backward

h.stage_1 = True

d = Debug("gearbox")
d._vocal = True

try:
    while True:
        time.sleep(0.2)
        #e-stop behavior
        if h.estop:
            d.level = 1
           
            h.spindle_motor = False
            if h.rpm_surveillance:
                h.spindle_break = True
            else:
                h.spindle_break = False
            
            h.block_1_forward = False
            h.block_1_backward = False
            h.block_2_forward = False
            h.block_2_backward = False
            h.block_3_forward = False
            h.block_3_backward = False

            soft_start_timer.stop()
            start_check_timer.stop()
            current_timer.stop()
            block_reset_timer.stop()
            block_spindle_timer.stop()

        else:

            #getting gearbox positions
            for block in ['block_1_', 'block_2_', 'block_3_']:
                b_1 = block + '1'
                b_2 = block + '2'
                
                state = 0
                if h[b_1] and h[b_2]:
                    h[block + 'pos'] = 1
                elif not h[b_1] and h[b_2]:
                    h[block + 'pos'] = 2
                elif h[b_1] and not h[b_2]:
                    h[block + 'pos'] = 3

                if h[block + 'cmd'] == 0:
                    h[block + 'cmd'] = h[block + 'pos']
                    h[block + 'set'] = True

    
            # starting / stopping spindle        
            if h.spindle_on or spindle_on:
                d.level = 2
               
                if h.reverse:
                    h.cw = False
                    h.ccw = True
                else:
                    h.cw = True
                    h.ccw = False
    
                h.spindle_break = False
                h.spindle_motor = True
                start_check_timer.start()
                if not start_check_timer():
                    if not h.rpm_surveillance:
                        c.error_msg("Spindle start: Spindle not turning.")
                    if not h.spindle_contactor: 
                        c.error_msg("Spindle start: Spindle contactor problem.")
    
                soft_start_timer.start()
                if soft_start_timer.alarm():
                    h.soft_start = True
    
            else:
                h.spindle_motor = False
                h.soft_start = False
                soft_start_timer.stop()
                h.cw = False
                h.ccw = False
    
                if h.rpm_surveillance:
                    h.spindle_break = True
                else:
                    h.spindle_break = False
    
            #setting gearbox
            if not h.spindle_on:
                
                for block in ['block_1_', 'block_2_', 'block_3_']:
                    
                    block_cmd = h[block + 'cmd']
                    block_pos = h[block + 'pos']
                    b_ = block
                    b_1 = block + '1'
                    b_2 = block + '2'
                    if h[block + 'cmd'] != h[block + 'pos']:
                        d.level = 4
                        h[b_ + 'set'] = False
                        break
                    else:
                        d.level = 5
                        h[b_ + 'forward'] = False
                        h[b_ + 'backward'] = False
                        h[b_ + 'set'] = True
                    
                #release any blockage
                if current_timer.alarm():
                    d.level = 6
                    block_reset_timer.start()

                    if block_reset_timer.alarm():
                        current_timer.stop()
                        print("A")

                    #identify jam type
                    if current_alarm_type == "":
                        if h[b_ + 'forward']:
                            current_alarm_type = "block_forward"
                        elif h[b_ + 'backward']:
                            current_alarm_type = "block_backward"
    
                    if current_alarm_type == "block_forward":
                        d.level = 20
                        h[b_ + 'forward'] = False
                        block_reset_timer.start()
                        if block_reset_timer():
                            d.level = 21
                            h[b_ + 'backward'] = True
                            continue
                        else:
                            d.level = 22
                            h[b_ + 'backward'] = False
                            block_spindle_timer.start()
                        
                    elif current_alarm_type == "block_backward":
                        d.level = 23
                        h[b_ + 'backward'] = False
                        block_reset_timer.start()
                        if block_reset_timer():
                            d.level = 24
                            h[b_ + 'forward'] = True
                            continue
                        else:
                            d.level = 25
                            h[b_ + 'forward'] = False
                            block_spindle_timer.start()
                            #continue
                        
                    if block_spindle_timer():
                        d.level = 26
                        spindle_on = True
                        continue
                    else:
                        spindle_on = False
    
                    d.level = 30
                    block_reset_timer.stop()
                    block_spindle_timer.stop()
                    current_alarm_type = ""
                    continue
    
                #Set the gearbox
                if block_cmd > block_pos:
                    d.level = 10
                    
                    h[b_ + 'forward'] = True
                    h[b_ + 'backward'] = False
                    if h.current_measurement:
                        current_timer.start()
                    else:
                        current_timer.stop()

                elif block_cmd < block_pos:
                    d.level = 11
                    
                    h[b_ + 'forward'] = False
                    h[b_ + 'backward'] = True
                    if h.current_measurement:
                        current_timer.start()
                    else:
                        current_timer.stop()
              


except KeyboardInterrupt:
    raise SystemExit
