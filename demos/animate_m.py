#!/usr/bin/env python3

'''
Let's animate the block M rotation video.
'''

import os
import glob

import matplotlib.pyplot as plt

from spacepy.pybats import bats


datadir = './'  # './IO2/'

mhd = bats.Bats2d(glob.glob(datadir + 'O2*.outs')[-1], blocksize=6)

ckwargs = {'add_body': False, 'add_cbar': False, 'zlim': [1.0, 2.0],
           'cmap': 'cividis', 'xlim': [-20, 20], 'ylim': [-20, 20]}


def plot_pcol_simple(mhd, title='BATS-R-US Advection', savedir=None):
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111)

    mhd.add_pcolor('x', 'y', 'rho', target=ax, **ckwargs)
    ax.text(0.02, 0.02, f"T={mhd.attrs['runtime']:08.6f}s", color='w',
            transform=ax.transAxes, size=20)
    ax.text(0.02, 0.96, "Density in a Circular Flow", color='w',
            transform=ax.transAxes, size=26)
    ax.text(0.02, 0.925, f"{title}", color='w',
            transform=ax.transAxes, size=22)
    fig.subplots_adjust(top=1, bottom=0, left=0, right=1)
    ax.set_aspect('equal')

    if savedir is not None:
        fig.savefig(savedir + f"frame_i{mhd.attrs['iframe']:05d}.png")


def plot_pcol_grid(mhd, title='BATS-R-US Advection', savedir=None):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(20, 10))
    fig.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=0, wspace=0)

    mhd.add_pcolor('x', 'y', 'rho', target=a1, **ckwargs)
    mhd.add_grid_plot(target=a2, do_label=False, cmap='Reds_r')  # 'viridis')
    a2.set_xlim(ckwargs['xlim'])
    a2.set_ylim(ckwargs['ylim'])
    a2.get_yaxis().set_visible(False)
    a2.set_ylabel('')

    a1.text(0.02, 0.02, f"T={mhd.attrs['runtime']:08.6f}s", color='w',
            transform=a1.transAxes, size=20)
    a1.text(0.02, 0.96, "Density in a Circular Flow", color='w',
            transform=a1.transAxes, size=26)
    a1.text(0.02, 0.925, f"{title}", color='w',
            transform=a1.transAxes, size=22)

    a1.set_aspect('equal')

    if savedir is not None:
        fig.savefig(savedir + f"frame_i{mhd.attrs['iframe']:05d}.png")


out1 = 'mhd_frames_simple/'
out2 = 'mhd_frames_grid/'

for out in [out1, out2]:
    if not os.path.exists(out):
        os.mkdir(out)

for i in range(mhd.attrs['nframe']):
    mhd.switch_frame(i)
    print(f"\tWorking on frame {i} of {mhd.attrs['nframe']}")
    plot_pcol_simple(mhd, title='BATS-R-US 2nd Order + AMR', savedir=out1)
    plot_pcol_grid(mhd, title='BATS-R-US 2nd Order + AMR', savedir=out2)
    if plt.isinteractive():
        break
    plt.close('all')
