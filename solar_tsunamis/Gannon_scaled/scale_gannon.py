#!/usr/bin/env python3

'''
Generate some extreme drivers based by scaling the Gannon storm.
'''

# Expand Pythonpath. Yes, this is not great...
import sys
import os
sys.path.insert(0, os.getcwd() + '/../../SEA_drivers/')

import datetime as dt

from spacepy.plot import style
from spacepy.pybats import ImfInput
from process_drivers import scale_imf

style()

# Variables to plot:
plotvars = [['bx', 'by'], 'bz', 'v', 'n', 't']

# Open base IMF file:
imf = ImfInput('./IMF_wind_propagated.dat')

# Key dates/times for scaling.
start = dt.datetime(2024, 5, 10, 17, 14)
stop = dt.datetime(2024, 5, 11, 18, 0)

# Loop over series of factors; scale plot and save.
for x in [1.5, 2, 5]:
    imf_ext, scale = scale_imf(imf, start, stop, 15, 720, amp=x)
    fig = imf_ext.quicklook(title=f'Gannon $\\times$ {x}', plotvars=plotvars)

    xstr = f"{x}".replace('.', 'p')
    fig.savefig(f'imf_scaled_{xstr}.png')
    imf_ext.write(f"imf_scaled_{xstr}.dat")