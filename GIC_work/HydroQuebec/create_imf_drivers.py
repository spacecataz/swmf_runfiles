#!/usr/bin/env python

'''
Let's make fake drivers for the 1989 storm event!  

TO USE THIS: RUN IN IPYTHON USING *run -i create_imf_drivers.py*
'''

# Make sure we're running in the correct mode:
try:
    __IPYTHON__
except:
    raise(ValueError('Please run in IPython mode'))

import datetime as dt

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np
from scipy.io import loadmat

from omni import read_ascii
from spacepy.datamodel import dmarray
from spacepy.pybats import kyoto as kt
from spacepy.pybats import ImfInput, apply_smart_timeticks

from smooth import smooth
from burton import burton_rk4

start = dt.datetime(1989, 3, 13, 0, 0, 0)
end   = dt.datetime(1989, 3, 16, 6, 0, 0)

# LOAD ALL RELEVANT DATA.
# Only load on first call.  THIS IS WHY WE USE RUN -I.

# Get observed Kyoto dst:
if ('dst' not in locals()) or ('dst' not in globals()):
    print('Fetching DST from Kyoto... please hold.')
    dst = kt.fetch('dst', [1989, 3], [1989, 3])
    dst['t'] = np.array([(x-start).total_seconds()/60.0 for x in dst['time']])
# Load omni data.
if ('omni' not in locals()) or ('omni' not in globals()):
    print('Loading OMNI data... please hold.')
    omni = read_ascii('./omni_min_3149.lst')
    omni['t'] = np.array([(x-start).total_seconds()/60.0 for x in omni['time']])

# Load SEA data.
sourcedir = '/Users/dwelling/projects/SEA_drivers/CME/SEA_MeanData/'
var = ['vx', 'rho', 'bx', 'by', 'bz', 'temp', 'dst']
fil = ['MeanNvx.mat', 'MeanNn.mat', 'MeanNBx.mat', 'MeanNBy.mat', 
       'MeanNBz.mat', 'MeanNT.mat', 'MeanNDst.mat']

sea = {}
sea['t'] = np.array(np.arange(6040.))
# Adjust time to match curve!
sea['t'] -= 459 # 459 Match SSC start.
loc = (sea['t']>86)&(sea['t']<=185) # match ssc end
sea['t'][loc] = [86.+(x-86.)*32./96. for x in sea['t'][loc]]
#
## Pull points to end of SSC.
t_contract = 641. - 459. - 118.
loc = sea['t'] > 119
sea['t'][loc] -= t_contract

## Line up storm max:
loc = sea['t']>118
sea['t'][loc] = [118.+(x-118.)*1367./801. for x in sea['t'][loc]]

## Collapse recovery to match:
loc = sea['t']>1486
sea['t'][loc] = [1486.+(x-1486.)* 3149./7694. for x in sea['t'][loc]]
#
# Load the data:
for v, f in zip(var, fil):
    sea[v] = loadmat(sourcedir+f)['Data'].reshape(6040)
    #if v != 'dst':
    #    sea[v] = smooth(sea[v], 30)
    
    
## shift the inital value of Dst:
shift = omni['SYM/H'][omni['t'] == 0] - sea['dst'][sea['t']==0]
sea['dst'] += shift

# Scale the data:
#ratio = (omni['SYM/H'].max() - omni['SYM/H'].min()) \
#        / (sea['dst'].max()  - sea['dst'].min())
#r1 = omni['SYM/H'].max() / sea['dst'].max()
base = sea['dst'][sea['t']==0]
r1 = (72.-20.) / (27.5-base) # Ratio of Dst jumps due to SSC.
r2 = omni['SYM/H'].min() / sea['dst'].min()
# Scale pre-storm values from baseline to new peak:
loc  = sea['dst']>=base #(sea['t']>85)&(sea['t']<200)#1485)
sea['dst'][loc] = [ base + (x-base)*r1 for x in sea['dst'][loc] ]
sea['dst'][sea['dst']<0] *= r2
sea['time'] = np.array([start+dt.timedelta(minutes=x) for x in sea['t']])

# Plot Dst comparison.
f1 = plt.figure()
ax = f1.add_subplot(111)
ax.plot(dst['t'], dst['dst'], label='Kyoto D$_{ST}$')
ax.plot(omni['t'], omni['SYM/H'], label='SYM-H')
ax.plot(sea['t'], sea['dst'], '.-', label='Adjusted SEA')
ax.set_xlim([0, 5040])
ax.legend(loc='best')
#ax.set_xlabel('Event Time ($Hours$)')
ax.set_xlabel('Event Time ($mins$)')
ax.set_ylabel('D$_{ST}$ ($nT$)')
#ax.xaxis.set_major_locator(MultipleLocator(24))
#ax.xaxis.set_minor_locator(MultipleLocator(6))
f1.tight_layout()
ax.grid()

# Turn SEA results into a IMF file:
# Create imf file.
imf1 = ImfInput('imf_SEA_reference.dat', load=False, npoints=6040)
imf2 = ImfInput('imf_hydroQuebec.dat',   load=False, npoints=6040)

# Create time:
imf1['time'] = np.array([start+dt.timedelta(minutes=x) for x in range(6040)])
imf2['time'] = np.array([start+dt.timedelta(minutes=x) for x in sea['t']])


# Fill file.
for v in var[:-1]:
    imf1[v] = dmarray(1.0*sea[v], {})
    imf2[v] = dmarray(1.0*sea[v], {})
imf1['ux']=imf1['vx']
imf2['ux']=imf2['vx']

# Save orig. data.
imf1.write()
imf1.quicklook()
plt.subplot(511).set_title('Original SEA Drivers', size=18)

# Save time shifted but not concatenated data.
imf1['time']=imf2['time']
imf1.attrs['file'] = './imf_HydroUnscaled.dat'
imf1.write()

# Scale IMF2 to get desired results.
# Main phase BZ: huge!
loc = sea['t']>108.0
imf2['bz'][loc] *= r2

imf2['ux']  = np.array([-440. + (x+440.)*3.5 for x in imf2['ux']] )
loc = imf2['rho'] > 8
imf2['rho'][loc] = np.array([ 8.00 + (x-8.00)*8. for x in imf2['rho'][loc]])
#loc = imf2['rho'] <= 4
#imf2['rho'][loc] = np.array([ 4.00 + (x-4.00)*2.5 for x in imf2['rho'][loc]])

# Plot edited IMF.
imf2.quicklook()
plt.subplot(511).set_title('Edited SEA Drivers', size=18)

# Have a look at the Mach number.  We can't go sub-alfvenic!
imf = imf2
imf.calc_alfmach()
fig =plt.figure(figsize=[7.5,10])
a1, a2 = fig.add_subplot(411), fig.add_subplot(412)
a3, a4 = fig.add_subplot(413), fig.add_subplot(414)
a1.plot(imf['time'],     imf['u'])
a2.plot(imf['time'],     imf['b'])
a3.plot(imf['time'],     imf['vAlf'])
a4.semilogy(imf['time'], imf['machA'])
loc = imf['machA']<=1.0
a4.semilogy(imf['time'][loc], imf['machA'][loc], 'r.')

# Save scaled data.
imf2.write()

# Use Burton equation to see how our IMF drivers perform!
print('Integrating Burton equation... please hold.')

tBurt1, dstBurt1 = burton_rk4(imf1.attrs['file'], dT=60.0)
tBurt2, dstBurt2 = burton_rk4(imf2.attrs['file'], dT=60.0)

f2 = plt.figure()
ax = f2.add_subplot(111)
ax.plot(dst['time'],  dst['dst'],    'k--', label='Kyoto D$_{ST}$')
ax.plot(omni['time'], omni['SYM/H'], 'k:',  label='SYM-H')
ax.plot(sea['time'],  sea['dst'],    'b--', label='Adjusted SEA')
ax.plot(tBurt1,       dstBurt1,      'r:',  label='Adj. SEA + Burton')
ax.plot(tBurt2,       dstBurt2,      'r-',  label='Scaled SEA + Burton')
ax.legend(loc='best')
ax.set_ylabel('D$_{ST}$ ($nT$)')
apply_smart_timeticks(ax, tBurt1, dolabel=True)
f2.tight_layout()
ax.grid()
