#!/usr/bin/env python
'''
Freeman & Morley's Minimal Substorm Model.  Calculate the energy in the tail vs.
time using solar input from a SWMF-formatted ascii solar wind file.
See Freeman and Morley 2004, GRL.

Can be imported as a module or run as a stand-alone script that, upon reading
an SWMF-formatted IMF file, calculates substorm occurrence and system energy
state.

Requires

Usage: msm.py imf_file [-h] [-D]
     ...where imf_file is the name of the file to be read.

Options:
-h or -H or -help:
    Print this help information.

-D=<value>:
    Change the substorm time constant.
'''

import os
import numpy as np
import matplotlib.pyplot as plt

from spacepy.pybats import ImfInput
from spacepy.plot import applySmartTimeTicks, style

from clasp605 import ImfData

import spacepy.plot as plot
plot.style()

# ##### BEGIN MAIN PROGRAM:

# Declare defaults constants:
D = 2.69 * 3600.  # Hours -> seconds

# Handle arguments:
for arg in sys.argv[1:]:
    if '-h' in arg.lower():
        # Print doc string to screen; quit.
        print(__doc__)
        exit()
    elif '-D' in arg:
        # Set time constant to non-default value
        D = float(arg[3:])
    else:
        filename = arg
        if not os.path.exists(filename):
            raise(ValueError('{} not a valid file.'.format(arg)))

# Open data file, calculate required values.
imf = ImfData(filename)
imf.calc_epsilon()

# Create results containers:
n_pts = imf['time'].size
energy = np.zeros(n_pts)
epochs = []

ener_last = D*imf['epsilon'].mean()
energy[0] -= ener_last

# Integrate:
for i in range(1, n_pts):
    dt = (imf['time'][i]-imf['time'][i-1]).total_seconds()
    energy[i] = energy[i-1]+imf['epsilon'][i]*dt

    if energy[i] >= 0:
        ener_last = D*imf['epsilon'][i]
        energy[i] = - ener_last
        epochs.append(imf['time'][i])

# Create figure object and axes objects.
fig = plt.figure()
a1, a2 = fig.add_subplot(211), fig.add_subplot(212)

# Create line plots:
a1.plot(imf['time'], imf['epsilon'], 'r-', lw=2)
a2.plot(imf['time'], energy,          '-', lw=2)

# Create and label horizontal threshold line:
a2.text(imf['time'][0], 0.05, 'Substorm Energy Threshold')
a2.hlines(0.0, imf['time'][0], imf['time'][-1], linestyles='dashed', lw=2.0)

# Place epochs onto plot, preserving y-limits.
ymin, ymax = a2.get_ylim()        # get current axis limits.
ymax = .2                         # add some space above zero.
a2.vlines(epochs, ymin, ymax)     # add our vlines.  This changes limits...
a2.set_ylim([ymin, ymax])       # restore ylimits to good values.

# Y-axes labels:
a1.set_ylabel('Solar Wind Power', size=14)
a2.set_ylabel('Tail Energy State', size=14)

# Y-axis ticks:
a1.set_yticklabels('')
a2.set_yticklabels('')

# Set time ticks:
applySmartTimeTicks(a1, imf['time'])
applySmartTimeTicks(a2, imf['time'], True)

fig.tight_layout()
