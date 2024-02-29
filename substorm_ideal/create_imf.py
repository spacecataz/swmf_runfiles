#!/usr/bin/env python3

import os
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
from spacepy.pybats import ImfInput
from spacepy.plot import applySmartTimeTicks, style

style()

# A twelve hour run:
t = np.arange(12.*60.)
start = dt.datetime(2000, 1, 1, 0, 0, 0)
time = np.array([start + dt.timedelta(minutes=m) for m in t])

# Create simple curves for every non-zero item.
dens = np.zeros(len(t))+10.0
temp = np.zeros(len(t))+100000.0
vx = np.zeros(len(t))-500.0

# Create some cool Bz curves:
names = []
bz = []

# Bz=-5 to -15 in ~20 minutes.
bz.append(-10/np.pi*np.arctan(np.pi/20.*(t-360.))-10.)
names.append('s5_s15_atan20')

# Bz=+5 to -15 in ~20 minutes
bz.append(-20/np.pi*np.arctan(np.pi/20.*(t-360.))-5.)
names.append('n5_s15_atan20')

# Bz=+5 to -15 in ~4 hours
bz.append(-20/np.pi*np.arctan(np.pi/240.*(t-360.))-5.)
names.append('n5_s15_atan240')

# Bz=+5 to -15 over 12 hours.
bz.append(-20./720. * t + 5.)
names.append('n5_s15_lin720')

# Bz impulsive +5 to -15 at t=6 hours.
bz.append(np.zeros(t.size)+5.)
bz[-1][t >= 360.] = -15.
names.append('n5_s10_step')

# Ask if we should overwrite existing files.
answer = input('Overwrite existing IMF files [y/N]?')
owrite = True if 'y' in answer.lower() else False

# Illustrate Bz curves, save imf files.
f = plt.figure(figsize=[10, 6])
ax = f.add_subplot(111)
for b, n in zip(bz, names):
    fname = 'imf_files/imf_ideal_{}.dat'.format(n)
    imf = ImfInput(fname, load=False, npoints=t.size)
    imf['rho'] = dens
    imf['ux'] = vx
    imf['temp'] = temp
    imf['bz'] = b
    imf['time'] = time
    if 'pram' in imf:
        imf.pop('pram')
    if not os.path.exists(fname) or owrite:
        imf.write()
    ax.plot(time, b, lw=2.5, label=n)

ax.legend(loc='best', ncol=2)
applySmartTimeTicks(ax, time)

xrng, yrng = np.array(ax.get_xlim()), 1.05*np.array(ax.get_ylim())
ax.hlines(0, time[0], time[-1], linestyles='dashed', colors='k', linewidth=2)
ax.vlines(start+dt.timedelta(hours=6), yrng[0], yrng[-1],
          linestyles='dotted', colors='k', linewidth=1)
ax.set_ylim(yrng)

ax.set_ylabel('B$_{Z}$ ($nT$)', size=16)
ax.set_xlabel('Simulation Time', size=16)
ax.set_title('IMF B$_Z$ Curves for Substorm Generation', size=20)
f.tight_layout()
if not os.path.exists('imf_files/imf_summary.png') or owrite:
    f.savefig('imf_files/imf_summary.png')

plt.show()