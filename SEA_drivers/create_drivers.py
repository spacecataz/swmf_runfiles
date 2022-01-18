#!/usr/bin/env python3

'''
This script reads the Katus et al. [2016] SEA data sets (not provided by this
repository!) and creates the initial SWMF input files.

For each "type" of storm (CIR, CME-SH, CME-MC), 4 files are made:
- Upstream drivers using SEA means
- Upstream drivers using SEA medians
- Hemispheric power index
- Dst (both mean and median).

Some notes: 
Raw data is assumed minute-level data.
HPI data is littered with NaNs; these are removed.
'''

import datetime as dt

import numpy as np
from scipy.io import loadmat

from spacepy.pybats import ImfInput

#### Constants/parameters ####
start = dt.datetime(2000,1,1,0,0,0) # First day/time of file.

var = ['ux', 'rho', 'bx', 'by', 'bz', 'temp']
fil = ['Nvx.mat', 'Nn.mat', 'NBx.mat', 'NBy.mat','NBz.mat', 'NT.mat']

# We need this header for IMF files...
imfheader = '''Data obtained via superposed epoch analysis performed by Katus et al. [2015] (https://doi.org/10.1002/2014JA020712)\n'''

# We need this header for HPI files...
hpiheader = '''# Prepared by the U.S. Dept. of Commerce, NOAA, Space Environment Center.
# Please send comments and suggestions to sec@sec.noaa.gov 
# 
# Source: NOAA POES (Whatever is aloft)
# Units: gigawatts

# Format:

# The first line of data contains the four-digit year of the data.
# Each following line is formatted as in this example:

# NOAA-12(S)  10031     9.0  4    .914

# Please note that if the first line of data in the file has a
# day-of-year of 365 (or 366) and a HHMM of greater than 2300, 
# that polar pass started at the end of the previous year and
# ended on day-of-year 001 of the current year.

# A7    NOAA POES Satellite number
# A3    (S) or (N) - hemisphere
# I3    Day of year
# I4    UT hour and minute
# F8.1  Estimated Hemispheric Power in gigawatts
# I3    Hemispheric Power Index (activity level)
# F8.3  Normalizing factor

'''

#### Functions ####
def write_hpi(time, hpi, filename):

    from numpy import log, isfinite

    # Filter out NaNs, other bad values:
    hpi[0]=hpi[1] # First value is always bad.
    time = time[np.isfinite(hpi)]
    hpi = hpi[np.isfinite(hpi)]
    
    with open(filename, 'w') as f:
        # Add header:
        f.write(hpiheader)
        f.write('{:04d}\n'.format(time[0].year))

        # Write rest of data entries
        for t, h in zip(time, hpi):
            doy = (t-time[0]).days+1
            ind = int(log(h)/log(1.6))
            f.write(f'NOAA-15(N){doy:03d}{t.hour:02d}{t.minute:02d}\t')
            f.write(f'{h:3.1f}\t{ind:d}\t1.0\n')

    return True

def write_dstlog(time, dstMean, dstMedian, filename):

    with open(filename, 'w') as f:
        f.write('SEA mean and median Dst values\n')
        f.write('year mo dy hr mn sc msc dstMean dstMedian\n')

        for t, d1, d2 in zip(time, dstMean, dstMedian):
            # Write time entry:
            f.write(f'{t:%Y %m %d %H %M %S} {t.microsecond/1000:03.0f} ')
            # Write data entry:
            f.write(f'{d1:13.5E} {d2:13.5E}\n')

#### MAIN SCRIPT BEGIN ####            
#### Request data location ####
print("Enter location of raw data (e.g., /users/uname/SEAdata/)")
data_dir = input() + '/'

# Create output files:
for prefix in ['CIR','SH','MC']:

    # Some convenience vars:
    meanpath = f'{data_dir}{prefix}/SEA_MeanData/'
    medipath = f'{data_dir}{prefix}/SEA_MedianData/'
    
    # Start by obtaining the size of the arrays:
    raw = loadmat(f'{meanpath}MeanNDst.mat')
    npts = raw['Data'].size

    # Assuming 1 minute separation, create time array:
    time = np.array([start+dt.timedelta(minutes=x) for x in range(npts)])

    # Create Dst output file:
    dstMean = raw['Data'].reshape(npts)
    dstMedi = loadmat(f'{medipath}MedianNDst.mat')['Data'].reshape(npts)
    write_dstlog(time, dstMean, dstMedi, f'dst_{prefix}_all.log')

    # Create HPI files:
    hpiMean = loadmat(f'{meanpath}MeanNhpi.mat')['Data'].reshape(npts)
    hpiMedi = loadmat(f'{medipath}MedianNhpi.mat')['Data'].reshape(npts)
    write_hpi(time, hpiMean, f'hpi_{prefix}_mean.txt')
    write_hpi(time, hpiMedi, f'hpi_{prefix}_median.txt')

    # Create IMF files:
    imfMean = ImfInput(f'imf_{prefix}_mean.dat', load=False, npoints=npts)
    imfMedi = ImfInput(f'imf_{prefix}_median.dat', load=False, npoints=npts)

    # Add header info:
    imfMean.attrs['header'].append(imfheader)
    imfMedi.attrs['header'].append(imfheader)
    
    # Add data values:
    imfMean['time'] = time
    imfMedi['time'] = time
    for v, f in zip (var, fil):
        imfMean[v] = loadmat(f'{meanpath}Mean{f}')['Data'].reshape(npts)
        imfMedi[v] = loadmat(f'{medipath}Median{f}')['Data'].reshape(npts)

    # Save 'em:
    imfMean.write()
    imfMedi.write()
