#!/usr/bin/env python3

'''
Generate some extreme drivers based on SH-type storms and
Tsurutani & Lahkina, 2014, amplitudes.
'''

import datetime as dt

from spacepy.pybats import ImfInput
from spacepy.plot import style
from process_drivers import scale_imf, smooth_imf

style()

plotvars = [['bx', 'by'], 'bz', 'v', 'n', 't']

# Open base data, apply some smoothing:
vsmooth = ['n', 't', 'ux', 'bx', 'by', 'bz']
imf_mean = smooth_imf('../sea_fullmin2023/imf_SH_mean.dat', vsmooth, window=15)
imf_medi = smooth_imf('../sea_fullmin2023/imf_SH_median.dat', vsmooth, window=15)

imf_medi.quicklook(title='SEA Medians', plotvars=plotvars)
imf_mean.quicklook(title='SEA Means', plotvars=plotvars)

# Set key dates for amplification
start = dt.datetime(2000, 1, 1, 8, 15, 0)
stop = dt.datetime(2000, 1, 1, 21, 0, 0)

# Set variable-based amplitudes
amps = {'ux': 4.05, 'uy': 4.05, 'uz': 4.05,
        'bx': 7.381, 'by': 7.381, 'bz': 7.381, 't': 4}

imf_ext1, scale = scale_imf(imf_medi, start, stop, 120, 720, amp=amps)
imf_ext1.quicklook(title='Median Extreme', plotvars=plotvars)

imf_ext2, scale = scale_imf(imf_mean, start, stop, 120, 720, amp=amps)
imf_ext2.quicklook(title='Mean Extreme', plotvars=plotvars)

# Based on the above plots, let's keep our Median Extreme.
imf_ext1.attrs['file'] = './imf_TS2014_KatusMedian.dat'
imf_ext1.write()