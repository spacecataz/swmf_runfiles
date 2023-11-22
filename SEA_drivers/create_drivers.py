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

import os
import datetime as dt
from glob import glob

import numpy as np
from scipy.io import savemat, loadmat

import matplotlib.pyplot as plt

from spacepy.plot import style
from spacepy.pybats import ImfInput

style()

# ### Constants/parameters ####
start = dt.datetime(2000, 1, 1, 0, 0, 0)  # First day/time of file.

var = ['ux', 'n', 'bx', 'by', 'bz', 't']
fil = ['Nvx.mat', 'Nn.mat', 'NBx.mat', 'NBy.mat', 'NBz.mat', 'NT.mat']

# We need this header for IMF files...
imfheader = 'Data obtained via superposed epoch analysis performed by ' + \
    'Katus et al. [2015] (https://doi.org/10.1002/2014JA020712)\n'

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


def write_hpi(time, hpi, filename):
    '''
    Write out the NOAA-formatted mean HPI file.
    '''

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


def load_masked(filename):
    '''
    Load a full masked array
    '''

    base = filename.split('/')[-1]
    fvar = base[1:-4]

    # Load data, mask invalid entries
    data = np.ma.masked_invalid(loadmat(filename)['Data'])

    # Magnetic field: bound to +/-60nT
    if fvar in ['Bx', 'By', 'Bz']:
        data[(data > 60)] = np.ma.masked
        data[(data < -55)] = np.ma.masked
    # Density: only positive values.
    if fvar == 'n':
        data[data < 0] = np.ma.masked
    # Temperature: above zero and not psychotic.
    if fvar == 'T':
        data[data < 0] = np.ma.masked
        data[data > 5e6] = np.ma.masked
    # Total V: above zero and not psychotic.
    if fvar == 'v':
        data[data < 0] = np.ma.masked
        data[data > 1500] = np.ma.masked
    # Vx: not psychotic.
    if fvar == 'vx':
        data[data < -1200] = np.ma.masked

    return data


def viz_rawdat(datadir, dsttype='SYMH', title='Data Summary'):
    '''
    Given a data dir (e.g., 'MC' or 'CME'), create a summary plot showing
    the individual event data and means/medians.

    Values plotted are 3 components of B, Vx, n, T, and Dst or SymH.

    Parameters
    ----------
    datadir : str
        Path of the data dir. Should contain files such as 'NBx.mat', etc.
    dsttype : str, defaults to 'SYMH'
        Set the type of Dst-like variable to plot. Should match .mat file name,
        e.g., 'N[dsttype].mat'.
    title : str, defaults to 'Data Summary'
        Plot title to place on figure.
    '''

    varnames = {'Bx': r'$B_X$ ($nT$)', 'By': r'$B_Y$ ($nT$)',
                'Bz': r'$B_Z$ ($nT$)', 'n': r'$n$ ($cm^{-3}$)',
                'v': r'$V$ ($km/s$)', 'T': r'$T$ ($K$)',
                dsttype: r'Dst ($nT$)'}

    fig = plt.figure(figsize=[11, 8.5])
    fig.suptitle(title, size=20)

    for i, v in enumerate(varnames):
        # Create axes:
        ax = fig.add_subplot(2, 4, i+1+1*(i > 2))

        # Open data, mask invalid values.
        data = load_masked(f'{datadir}/N{v}.mat')

        # Plot, label, etc.
        ax.plot(data, c='k', alpha=.25, label='_')
        l1, = ax.plot(data.mean(axis=1), lw=2.5, label='Mean')
        l2, = ax.plot(np.ma.median(data, axis=1), lw=1.5, label='Median')
        ax.set_xlabel('SEA Time ($m$)')
        ax.set_ylabel(varnames[v])

    fig.legend(handles=[l1, l2], bbox_to_anchor=[.75, .65, .2, .2])
    fig.tight_layout()

    return fig


# ### MAIN SCRIPT BEGIN ####
# ### Request data location ####
print("Enter location of raw data (e.g., " +
      "/users/uname/SEAdata/), enter X to exit")
data_dir = input() + '/'
if data_dir[0] == 'X':
    exit()

do_gen_means = 'y' in input("Generate means and medians?").lower()
do_plot = 'y' in input("Generate summary plots for raw data?").lower()

# Create output files:
for prefix in ['CIR', 'SH', 'MC', 'CME']:

    # Some convenience vars:
    basepath = f'{data_dir}{prefix}/'
    meanpath = f'{basepath}SEA_MeanData/'
    medipath = f'{basepath}SEA_MedianData/'

    # If directory not found, print and leave.
    if not os.path.exists(basepath):
        print(f'Directory {basepath} not found.')
        continue

    # Plot summary:
    if do_plot:
        dsttype = 'SYMH' if os.path.exists(f'{basepath}NSYMH.mat') else 'Dst'
        fig = viz_rawdat(basepath, dsttype, f'{prefix} Data Summary')
        fig.savefig(f"{basepath}summary_data.png")

    if do_gen_means:
        # Create mean/median directory if it doesn't exist.
        if not os.path.exists(meanpath):
            os.mkdir(meanpath)
        if not os.path.exists(medipath):
            os.mkdir(medipath)

        # Create a TXT report file.
        log = open(f'{basepath}gen_mean_log.txt', 'w')

        # Find all files to average:
        matfiles = glob(basepath + '*.mat')
        for f in matfiles:
            # Don't touch the date file.
            if 'NDate' in f:
                continue

            # Load and mask data.
            data = load_masked(f)

            # Create mean/median files:
            mean = data.mean(axis=1)
            medi = np.ma.median(data, axis=1)

            # Save .mat files:
            filebase = f.split('/')[-1]
            savemat(f'{meanpath}Mean{filebase}', {'Data': mean})
            savemat(f'{medipath}Median{filebase}', {'Data': medi})

            # Save information in log:
            ntotal = data.size
            nbad = np.sum(data.mask * 1)
            frac = 100 * nbad/ntotal
            log.write(f'File {f}:\n\t{ntotal} points, {nbad} NaNs ({frac:.2}%)\n')

        log.close()

    # Start by obtaining the size of the arrays:
    raw = loadmat(f'{meanpath}MeanNDst.mat')
    npts = raw['Data'].size

    # Assuming 1 minute separation, create time array:
    time = np.array([start+dt.timedelta(minutes=x) for x in range(npts)])

    # Create Dst output file:
    dstMean = raw['Data'].reshape(npts)
    dstMedi = loadmat(f'{medipath}MedianNDst.mat')['Data'].reshape(npts)
    write_dstlog(time, dstMean, dstMedi, f'dst_{prefix}_all.log')

    # Create SymH output file:
    if os.path.exists(f'{meanpath}MeanNSYMH.mat'):
        dstMean = loadmat(f'{meanpath}MeanNSYMH.mat')['Data'].reshape(npts)
        dstMedi = loadmat(f'{medipath}MedianNSYMH.mat')['Data'].reshape(npts)
        write_dstlog(time, dstMean, dstMedi,
                     f'{basepath}symh_{prefix}_all.log')

    # Create HPI files:
    if os.path.exists(f'{meanpath}MeanNhpi.mat'):
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
    for v, f in zip(var, fil):
        imfMean[v] = loadmat(f'{meanpath}Mean{f}')['Data'].reshape(npts)
        imfMedi[v] = loadmat(f'{medipath}Median{f}')['Data'].reshape(npts)

    # Save 'em:
    imfMean.write()
    imfMedi.write()
