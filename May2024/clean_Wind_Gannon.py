#!/usr/bin/env python
'''
A script to clean up the Wind MFI and SWE data
from the Gannon storm period. This is very much
a use-case specific example, with lots of hard-
coding. 
'''

import sys
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
#from scipy.signal import find_peaks
from scipy.constants import k, m_p

from spacepy import pycdf
from spacepy.plot import style, applySmartTimeTicks

# Turn on Spacepy style
style()

# Grab the files from the command line (uncomplicated):
mfi_file = sys.argv[1]
swe_file = sys.argv[2]

# Read the data from the CDF files:
mfi = pycdf.CDF(mfi_file)
mfi.readonly(False)
swe = pycdf.CDF(swe_file)
swe.readonly(False)

# Set NaN values for density and thermal speed:
for key in ['Np', 'THERMAL_SPD']:
    # Unfortunately, fancy indexing doesn't work here:
    for i, n in enumerate(swe[key]):
        if n < 0.:
            swe[key][i] = np.nan

# Separate bulk velocity components and set NaNs:
for j, comp in enumerate('XYZ'):
    var = swe['V_GSM'][:,j]
    for i, n in enumerate(var):
        if n + 9.9999998e+30 < 200:
            var[i] = np.nan
    swe['V'+comp] = var

# Now for the manual removal of spikes for each parameter.
# VX:
for i, n in enumerate(swe['VX']):
    if n > -390.: # positive peaks
        swe['VX'][i] = np.nan
    elif (swe['Epoch'][i] < swe['Epoch'][800]) & (n < -475.):
        # just the first 15 hours
        swe['VX'][i] = np.nan
    elif (swe['Epoch'][i].hour ==23) & (n > -700.):
        # for the one peak later
        swe['VX'][i] = np.nan
    else:
        pass

# VY:
for i, n in enumerate(swe['VY']):
    if (swe['Epoch'][i] < swe['Epoch'][800]) & (n > 40.):
        # for the positive peaks, first 15 hours
        swe['VY'][i] = np.nan
    elif (swe['Epoch'][i] < swe['Epoch'][800]) & (n < -38.):
        # for the negative peaks, first 15 hours
        swe['VY'][i] = np.nan
    elif (swe['Epoch'][i] > swe['Epoch'][800]) & (n < -100.):
        # for the later negative peaks
        swe['VY'][i] = np.nan
    else:
        pass
#print(swe['Epoch'][800])
# VZ:
for i, n in enumerate(swe['VZ']):
    if (swe['Epoch'][i] < swe['Epoch'][800]) & (n > 30.):
        # for the positive peaks, first 15 hours
        swe['VZ'][i] = np.nan
    elif (swe['Epoch'][i] < swe['Epoch'][1900]) & (n < -60.):
        # for the negative peaks, first 26 hours
        swe['VZ'][i] = np.nan
    elif (swe['Epoch'][i] > swe['Epoch'][800]) & (n < -158.):
        # for the later negative peaks
        swe['VZ'][i] = np.nan
    elif (swe['Epoch'][i].hour ==7) & (n > 100.):
        # for a later positive peak
        swe['VZ'][i] = np.nan
    else:
        pass

# Density:
for i, n in enumerate(swe['Np']):
    if (swe['Epoch'][i] < swe['Epoch'][800]) & (n > 15.):
        # for the first 15 hours
        swe['Np'][i] = np.nan

# Thermal Speed:
for i, n in enumerate(swe['THERMAL_SPD']):
    if (swe['Epoch'][i] < swe['Epoch'][800]) & (n < 20.):
        # for the first 15 hours
        swe['THERMAL_SPD'][i] = np.nan

# Convert thermal speed to temperature in Kelvin:
swe['TEMP'] = (m_p/(2*k))*(swe['THERMAL_SPD'][...]*1000)**2

# Make plots to test:
fig, axs = plt.subplots(8, 1, figsize=(10, 12), sharex=True)

for i, var in enumerate(['Np','TEMP', 'VX', 'VY', 'VZ']):
    axs[i].plot(swe['Epoch'], swe[var])
    axs[i].set_ylabel(var)
    applySmartTimeTicks(axs[i], swe['Epoch'], dolabel=False)

# Split up B components and set NaNs:
for j, comp in enumerate('XYZ'):
    b = mfi['BGSM'][:,j]
    p = mfi['PGSM'][:,j]
    for i, n in enumerate(b):
        if n + 9.9999998e+30 < 200:
            b[i] = np.nan
    mfi['B'+comp] = b
    mfi[comp+'GSM'] = p

for i, var in enumerate(['BX', 'BY', 'BZ']):
    axs[i+5].plot(mfi['Epoch'], mfi[var])
    axs[i+5].set_ylabel(var)
    applySmartTimeTicks(axs[i], swe['Epoch'], dolabel=False)

plt.savefig('20240510_wind_check.png')


# Create a dataframe for the SWE data:
import pandas as pd
swedf =  pd.DataFrame(np.vstack((swe['Np'],swe['TEMP'], swe['VX'],
                                 swe['VY'], swe['VZ'])).transpose(),
                      index=swe['Epoch'], columns=['Np','TEMP', 'VX', 'VY', 'VZ'])
swedf = swedf[~swedf.index.duplicated(keep='first')]

# Test plot:
#swedf.plot(subplots=True)

# Resample SWE data to match MFI (one minute):
swedf = swedf.resample('30s').mean()
swedf = swedf.interpolate(method='linear')
swedf = swedf.resample('60s').mean()
cutoff = datetime.strptime('2024-05-10 00:00:00', '%Y-%m-%d %H:%M:%S')
swedf = swedf.drop(swedf.loc[(swedf.index < cutoff)].index)
#print(swedf)
# Test plot:
#swedf.plot(subplots=True)
#plt.show()

# Combine MFI and SWE data into one CDF and save
wind = pycdf.CDF('20240510_wind_cleaned.cdf', '')
wind['Epoch'] = mfi['Epoch']

for var in ['Np','TEMP', 'VX', 'VY', 'VZ']:
    wind[var] = swedf[var]
for var in ['BX', 'BY', 'BZ', 'XGSM', 'YGSM', 'ZGSM']:
    wind[var] = mfi[var]

print(wind)
wind.close()
