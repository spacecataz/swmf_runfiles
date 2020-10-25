#!/usr/bin/env python


# DON'T USE THIS.  IMPORT OMNI OMNI.OMNI_TO_SWMF.

import datetime as dt
import numpy as np
from spacepy.pybats import ImfInput

raise Exception("DON'T USE THIS YOU IDIOT.")

def fix(arr, flag):
    '''
    For data vector 'arr', interpolate (linearly) over all regions where
    the the bad data flag, 'flag', is set.
    '''

    x = np.arange(arr.size)
    locs = arr!=flag

    return np.interp(x, x[locs], arr[locs])

raw = np.loadtxt('./omni_min_31756.lst')

# Convert time.
start = dt.datetime(int(raw[0,0]), 1,1,0,0,0)

time = np.zeros(raw.shape[0], dtype=object)

for i in range(raw.shape[0]):
    time[i] = start+dt.timedelta(days =int(raw[i,1])-1,
                                 hours=int(raw[i,2]), minutes=int(raw[i,3]))

# Create imf object:
imf = ImfInput(filename='imf_input.dat', load=False)

# Populate:
imf['time'] = time
imf['bx'], imf['by'], imf['bz'] = \
    fix(raw[:,5],9999.99), fix(raw[:,6],9999.99),  fix(raw[:,7],9999.99)
imf['ux'], imf['uy'], imf['uz'] = \
    fix(raw[:,9],99999.9), fix(raw[:,10],99999.9), fix(raw[:,11],99999.9)
imf['rho']  = fix(raw[:,-2], 999.99)
imf['temp'] = fix(raw[:,-1], 9999999.)

imf.pop('pram')
imf.write()
