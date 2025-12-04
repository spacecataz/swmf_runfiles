#!/usr/bin/env python3

'''
Convert a heliospheric virtual satellite to a magnetospheric solar wind
and IMF input file.
'''

from spacepy.pybats import ImfInput
from spacepy.pybats.bats import VirtSat

sat = VirtSat('./1au_mesoscale_point4.dat')

