#!/usr/bin/env python3

'''
Create and save a set of figures illustrating the SEA drivers and Dst.
'''

# import matplotlib.pyplot as plt

from spacepy.plot import style
from spacepy.pybats import ImfInput

style()

for prefix in ['CIR', 'SH', 'MC']:

    # Open the IMF files:
    imfMean = ImfInput(f'imf_{prefix}_mean.dat')
    imfMedi = ImfInput(f'imf_{prefix}_median.dat')

    # Create initial figure:
    fig = imfMean.quicklook(plotvars=['bx', 'by', 'bz', 'n', 'v'])
    fig.axes[0].set_title(f'SEA Drivers for {prefix} Events')

    # Add median curves to each axes:
    for v, ax in zip(['bx', 'by', 'bz', 'n', 'v'], fig.axes):
        ax.plot(imfMedi['time'], imfMedi[v], alpha=.7)

    ax.legend(['SEA Mean', 'SEA Median'], loc='best')
