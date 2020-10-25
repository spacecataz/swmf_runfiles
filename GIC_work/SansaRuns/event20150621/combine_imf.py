#!/usr/bin/env python

'''
Combine the Uz, Uy from the raw ACE/SWEPAM data (CDAWeb propagated w/ IDL)
with the high-quality density, Ux from OMNI.

These values have some very bad sections which need to be replaced.
'''

from datetime import datetime as dt

import numpy as np
import matplotlib.pyplot as plt

from validate import pairtimeseries_linear as pair
from spacepy.pybats import ImfInput

# Open data.  Do not repeat if using ipython interactively:
if 'imf_om' not in globals():
    imf_om = ImfInput('./imf20150620_omni.dat')
    imf_ac = ImfInput('./imf20150620_ace.dat')


# Change output file name for omni data:
imf_om.attrs['file'] = 'imf20150620.dat'

# Kill bad data:
loc1 = (imf_ac['time']>dt(2015,6,20,13, 6,10)) & \
       (imf_ac['time']<dt(2015,6,20,18,42,53))
loc2 = (imf_ac['time']>dt(2015,6,23,17, 0,30)) & \
       (imf_ac['time']<dt(2015,6,23,18, 0,23))
loc_all = np.zeros(loc1.size, dtype=bool) + True
loc_all[loc1] = False
loc_all[loc2] = False

for x in ['uy', 'uz']:
    # Interpolate over bad data:
    imf_om[x] = pair(imf_ac['time'][loc_all], imf_ac[x][loc_all],
                     imf_om['time'],fill_value='extrapolate')

imf_om.write()
    
