#!/usr/bin/env python

'''
Let's take a look at this event in terms of solar wind and IMF.
'''

import datetime as dt

import matplotlib.pyplot as plt
from spacepy.pybats import ImfInput, kyoto
from spacepy.plot   import style, applySmartTimeTicks

style()

# Set start and stop times for the simulation:
start = dt.datetime(2015,3,15, 0,0,0)
stop  = dt.datetime(2015,3,20, 0,0,0)

# Collect relevant data:
if 'dst' not in globals():
    imf = ImfInput('./IMF.dat')
    dst = kyoto.fetch('dst', start, stop)
    sym = kyoto.fetch('sym', start, stop)
    kp  = kyoto.fetch('kp' , start, stop)

# Plot solar wind:
f1 = imf.quicklook([start, stop])

# Plot indices:
f2 = plt.figure()
a1, a2 = f2.add_subplot(211), f2.add_subplot(212)
a1.plot(sym['time'], sym['sym-h'])
a1.plot(dst['time'], dst['dst'])
applySmartTimeTicks(a1, [start, stop])
kp.add_histplot(target=a2, time_range=[start, stop])

plt.show()
