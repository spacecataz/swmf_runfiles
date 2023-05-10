#!/usr/bin/env python3

'''
This code combines the SWEPAM STI data with the high-resolution magnetometer
data.
'''


def read_sti():
    '''
    Read the ACE STI data.
    '''

    with open('./ACE_raw_2001308.dat', 'r') as f:
        # Skip header:
        line = f.readline()
        while line[:5] != ' 2001':
            line = f.readline()

        # Slurp rest of lines:
        lines = line + f.readlines()

