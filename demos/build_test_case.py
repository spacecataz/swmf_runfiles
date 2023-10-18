#!/usr/bin/env python3

'''
Re-build edge case block.

Pre 6-9-2023, some pcolor plots failed for the rotating M animation.
This snippet reproduces the grid configuration for testing and fixing.
'''

import numpy as np
import matplotlib.pyplot as plt

from spacepy.pybats import qotree

blocksize = 4
dx1, dx2, dx3 = 1, 0.5, 0.25

prop_cycle = plt.rcParams['axes.prop_cycle']
colors = 10 * prop_cycle.by_key()['color']


def make_region(xstart, ystart, nblockx, nblocky, dx, ax=None):
    '''
    Create a region of points starting at "start".
    '''

    xstart += dx/2
    ystart += dx/2

    x = np.arange(xstart, xstart + nblockx*blocksize*dx, dx)
    y = np.arange(ystart, ystart + nblocky*blocksize*dx, dx)

    xall, yall = np.meshgrid(x, y)

    if ax is not None:
        ax.plot(xall, yall, '.', c=colors.pop(0))

    return np.meshgrid(x, y)

fig, ax = plt.subplots(1, 1)
ax.set_aspect('equal')
regions = []
regions.append(make_region(0, 0, 2, 8, dx2, ax=ax))
regions.append(make_region(4, 12, 3, 1, dx1, ax=ax))
regions.append(make_region(4, 8, 2, 1, dx1, ax))
regions.append(make_region(4, 0, 1, 2, dx1, ax))
regions.append(make_region(8, 0, 2, 4, dx2, ax))
regions.append(make_region(12, 8, 2, 2, dx2, ax))
regions.append(make_region(12, 6, 1, 1, dx2, ax))
regions.append(make_region(14, 6, 2, 2, dx3, ax))
regions.append(make_region(12, 0, 4, 6, dx3, ax))

xall, yall = np.zeros(0), np.zeros(0)
for x, y in regions:
    xall = np.append(xall, x.flatten())
    yall = np.append(yall, y.flatten())

tree = qotree.QTree(np.array([xall, yall]), blocksize=4)
tree.plot_res(ax)
tree[1].plotbox(ax)