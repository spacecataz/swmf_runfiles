#!/usr/bin/env python3

'''
This script generates the input IMF/solar wind drivers for the
idealized events.
'''

import imp
import datetime as dt
from spacepy.pybats import ImfInput

# Load the requisite data using an relative path:
pd = imp.load_source('process_drivers', '../../SEA_drivers/process_drivers.py')

# Open the raw SEA data file:
imf = ImfInput('../../SEA_drivers/imf_SH_mean.dat')

# Set epochs for scaling:
start = dt.datetime(2000,1,1,8,15,0)
stop = dt.datetime(2000,1,1,21,0,0)

# Smooth the solar wind velocity; scale data:
imf_default = pd.smooth_imf(imf, window=61)
imf_5x, scale = pd.scale_imf(imf_default, start, stop, 120, 720)

imf_default.attrs['file'] = 'imf_SH.dat'
imf_5x.attrs['file'] = 'imf_SH_5x.dat'

imf_default.write()
imf_5x.write()
