#!/usr/bin/env python

import hal
import time
import linuxcnc
from linuxcnc_timer import Timer
from debug import Debug

c = linuxcnc.command()

h = hal.component("gearbox_sim")

h.newpin("block_1_forward", hal.HAL_BIT, hal.HAL_IN)
h.newpin("block_1_backward", hal.HAL_BIT, hal.HAL_IN)
h.newpin("block_2_forward", hal.HAL_BIT, hal.HAL_IN)
h.newpin("block_2_backward", hal.HAL_BIT, hal.HAL_IN)
h.newpin("block_3_forward", hal.HAL_BIT, hal.HAL_IN)
h.newpin("block_3_backward", hal.HAL_BIT, hal.HAL_IN)

h.newpin("block_1_1", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("block_1_2", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("block_2_1", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("block_2_2", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("block_3_1", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("block_3_2", hal.HAL_BIT, hal.HAL_OUT)

h.ready()

block_1_pos = 1
block_2_pos = 2
block_3_pos = 3

block_1_timer = Timer(1.0)
block_2_timer = Timer(1.0)
block_3_timer = Timer(1.0)

d = Debug("gearbox_sim")
d._vocal = True

try:
    while True:

        #set gearpox output signals
        for block in ['block_1_', 'block_2_', 'block_3_']:
            if locals()[block + 'pos'] == 1:
                h[block + '1'] = True
                h[block + '2'] = True
            elif locals()[block + 'pos'] == 2:
                h[block + '1'] = False
                h[block + '2'] = True
            elif locals()[block + 'pos'] == 3:
                h[block + '1'] = True
                h[block + '2'] = False

        for block in ['block_1_', 'block_2_', 'block_3_']:
            if h[block + 'forward'] == True:
                d.level = 1
                locals()[block + 'timer'].start()

                if locals()[block + 'timer'].alarm():
                    d.level = 11
                    locals()[block + 'pos'] += 1

            elif h[block + 'backward'] == True:
                d.level = 2
                locals()[block + 'timer'].start()
                
                if locals()[block + 'timer'].alarm():
                    d.level = 12
                    locals()[block + 'pos'] -= 1

            else:
                locals()[block + 'timer'].stop()
       
except KeyboardInterrupt:
    raise SystemExit
