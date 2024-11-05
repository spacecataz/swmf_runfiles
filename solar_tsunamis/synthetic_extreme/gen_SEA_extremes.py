#!/usr/bin/env python3

'''
Generate some extreme drivers based on SH-type storms and
amplitudes from a number of sources.
'''

# Add SEA library to path:
import sys

import datetime as dt

from spacepy.plot import style

sys.path.append('../../SEA_drivers')
from process_drivers import scale_imf, smooth_imf

style()

plotvars = [['bx', 'by'], 'bz', 'v', 'n', 't']
rise, fall = 120, 720

# Open base data, apply some smoothing:
vsmooth = ['n', 't', 'ux', 'bx', 'by', 'bz']
path = '../../SEA_drivers/sea_fullmin2023/'
imf_mean = smooth_imf(path + '/imf_SH_mean.dat', vsmooth, window=15)
imf_medi = smooth_imf(path + '/imf_SH_median.dat', vsmooth, window=15)

imf_medi.quicklook(title='SEA Medians', plotvars=plotvars)
imf_mean.quicklook(title='SEA Means', plotvars=plotvars)

# Set key dates for amplification
start = dt.datetime(2000, 1, 1, 8, 15, 0)
stop = dt.datetime(2000, 1, 1, 21, 0, 0)

# Set storm names, output files, and amplitudes:
names = ['TS2014', 'G100', 'G1000']

# Set variable-based amplitudes.
amps = {'TS2014': {'ux': 4.05, 'uy': 4.05, 'uz': 4.05,
                   'bx': 7.381, 'by': 7.381, 'bz': 7.381, 't': 4},
        'G100': {'ux': 4.05, 'uy': 4.05, 'uz': 4.05,
                 'bx': 7.381, 'by': 7.381, 'bz': 7.381, 't': 4},
        'G1000': {'ux': 4.05, 'uy': 4.05, 'uz': 4.05,
                  'bx': 7.381, 'by': 7.381, 'bz': 7.381, 't': 4}}

# Create scaled drivers:
for n in names:
    # Perform Median-based extreme.
    imf, scale = scale_imf(imf_medi, start, stop, rise, fall, amp=amps[n])
    imf.quicklook(title=f'SEA Median-Based Extreme: {n}',
                  plotvars=plotvars)
    imf.attrs['file'] = f'./imf_{n}_KatusMedian.dat'
    imf.write()

    # Perform Mean-based extreme.
    imf, scale = scale_imf(imf_mean, start, stop, rise, fall, amp=amps[n])
    imf.quicklook(title=f'SEA Mean-Based Extreme: {n}',
                  plotvars=plotvars)
    imf.attrs['file'] = f'./imf_{n}_KatusMean.dat'
    imf.write()
