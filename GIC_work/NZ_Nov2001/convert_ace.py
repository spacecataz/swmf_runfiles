#!/usr/bin/env python3

'''
This code combines the SWEPAM STI data with the high-resolution magnetometer
data.
'''

from datetime import datetime, timedelta
import numpy as np
from numpy.ma import masked_less


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
        data['time'][i] += timedelta(days=float(parts[1]) + float(parts[2]))

        for j, v in enumerate(varnames):
            data[v][i] = parts[j+3]

    # Mask bad data:
    for v in varnames:
        data[v] = masked_less(data[v], badval)

    return data
