#!/usr/bin/env python3

'''
This code combines the SWEPAM STI data with the high-resolution magnetometer
data.

SWEPAM STI was provided by Ruth Skoug, LANL.
MAG data was obtained via NASA CDAWeb.

L1 to bowshock timeshift was obtained by comparing IMF values from OMNIWeb
to ACE/unshifted. Yes, this is a hack, but it's better than nothing.
'''

from datetime import datetime, timedelta

import numpy as np
from numpy.ma import masked_less
import matplotlib.pyplot as plt

from spacepy.pycdf import CDF
from spacepy.plot import style, applySmartTimeTicks

import omni as om

# Time shift between OMNI and ACE Raw (obtained using OMNI data and peak Bz)
tshift = timedelta(seconds=-2212.00416)  # seconds

# Desired time range:
tlim = [datetime(2001, 11, 5, 0, 0, 0),
        datetime(2001, 11, 9, 0, 0, 0)]


def load_ace_cdf():
    '''
    Load the high-quality ACE data from CDF.
    '''

    raw = CDF('./ac_h0s_mfi_20011105.cdf')

    data = {}
    data['time'] = raw['Epoch'][...]
    for i, b in enumerate('xyz'):
        data['b' + b] = masked_less(raw['BGSM'][:, i], -1e10)

    return data


def load_ace_sti():
    '''
    Read the ACE STI data file and parse into
    '''

    badval = -9999
    varnames = ['n', 't', 'v', 'vx', 'vy', 'vz', 'b', 'bx', 'by', 'bz']

    with open('./ACE_raw_2001308.dat', 'r') as f:
        # Skip header:
        line = f.readline()
        while line[:5] != ' 2001':
            line = f.readline()

        # Slurp rest of lines:
        lines = [line] + f.readlines()

    # Create data container.
    nlines = len(lines)
    data = {}
    data['time'] = np.zeros(nlines, dtype=object)
    for v in varnames:
        data[v] = np.zeros(nlines)

    # Loop over lines, parse data.
    for i, l in enumerate(lines):
        parts = l.split()

        # Time entry:
        data['time'][i] = datetime(int(parts[0]), 1, 1, 0, 0, 0)
        data['time'][i] += timedelta(days=float(parts[1])+float(parts[2])-1)

        for j, v in enumerate(varnames):
            data[v][i] = parts[j+3]

    # Mask bad data:
    for v in varnames:
        data[v] = masked_less(data[v], badval)

    return data


if __name__ == '__main__':
    '''Perform conversion; create relevant plots.'''
    sti = load_ace_sti()
    mag = load_ace_cdf()
    omn = om.read_ascii('./omni_20011106.fmt')

    style()

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 7))

    a1.plot(mag['time'], mag['bz'], label='ACE/CDAWeb')
    a1.plot(sti['time'], sti['bz'], label='ACE/STI Available')
    applySmartTimeTicks(a1, tlim, dolabel=False)
    a1.set_ylabel('IMF B$_Z$ ($nT$)')
    a1.legend(loc='best')

    a2.plot(sti['time'], sti['n'], label='ACE/STI Available')
    a2.plot(omn['time'] + tshift, omn['Proton Density'], label='OMNIWeb')
    applySmartTimeTicks(a2, tlim, dolabel=True)
    a2.set_ylabel('Density ($cm^{{-3}}$)')
    a2.legend(loc='best')

    fig.tight_layout()