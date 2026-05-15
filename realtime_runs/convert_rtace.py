#!/usr/bin/env python3

'''
Convert a set of MAG and SWEPAM ASCII files from the ACE real time FTP
data server into an (unpropagated) SWMF input file.

This script requires `swtools` from SWMF_helpers.
'''

from argparse import ArgumentParser, RawDescriptionHelpFormatter
import datetime as dt
import numpy as np

from spacepy.pybats import ImfInput

from swtools import pair, l1_propagate


parser = ArgumentParser(description=__doc__,
                        formatter_class=RawDescriptionHelpFormatter)
parser.add_argument('-m', '--mag', nargs='+', help='MAG files to convert. ' +
                    'Can be a single file or Unix wildcard pattern.')
parser.add_argument('-s', '--swe', nargs='+', help='SWEPAM files to convert. '
                    + 'Can be a single file or Unix wildcard pattern.')
parser.add_argument('-o', '--outfile', type=str, default='imf_ace.dat',
                    help='Name of output IMF file.')
parser.add_argument('-p', '--propagate', action='store_true', default=False,
                    help='Propagate from L1 to SWMF upstream boundary.')
parser.add_argument("-sm", "--smoothing", default=11, type=int,
                    help="Velocity may be smoothed via median filtering. " +
                    "Set this argument to an integer window size to apply " +
                    "smoothing. Default is 11 points, or moderate smoothing.")


# Handle arguments, noting that argparse expands linux wildcards.
args = parser.parse_args()

s_vars = ['n', 'ux', 't']
m_vars = ['bx', 'by', 'bz']


def read_ace_ascii(filein, ftype='mag'):
    '''
    Load a MAG or SWEPAM ASCII file into a dictionary of Numpy arrays.
    Use `ftype` kwarg to specify MAG (mag) or SWEPAM (swe) data file.
    '''

    # Set variable group:
    varnames = s_vars if ftype == 'swe' else m_vars

    # Open, slurp contents,
    with open(filein, 'r') as f:
        line = f.readline()
        while '#----' not in line:
            line = f.readline()

        lines = f.readlines()

    # Create container
    npts = len(lines)
    out = {'time': np.zeros(npts, dtype=object)}
    for v in varnames:
        out[v] = np.zeros(npts)

    for i, l in enumerate(lines):
        parts = l.split()

        # Set time:
        yy, mm, dd = int(parts[0]), int(parts[1]), int(parts[2])
        hh, mn = int(parts[3][:2]), int(parts[3][2:])
        out['time'][i] = dt.datetime(yy, mm, dd, hh, mn, 0)

        # Save variables:
        for j, v in enumerate(varnames):
            out[v][i] = parts[7 + j]

    # Flip sign on velocity to get Ux:
    if ftype == 'swe':
        out['ux'] *= -1

    return out


# Ensure we have lists of file names:
if type(args.swe) is not list:
    args.swe = [args.swe]
if type(args.mag) is not list:
    args.mag = [args.mag]

# Sort and pair files together:
args.swe.sort()
args.mag.sort()

# Check number of files:
if len(args.swe) != len(args.mag):
    raise ValueError('Number of SWEPAM and MAG files is not equal.')

# Open first file:
f_swe, f_mag = args.swe.pop(0), args.mag.pop(0)
swe, mag = read_ace_ascii(f_swe, 'swe'), read_ace_ascii(f_mag, 'mag')

# Open remaining files and combine data:
for f_swe, f_mag in zip(args.swe, args.mag):
    swe_now = read_ace_ascii(f_swe, 'swe')
    mag_now = read_ace_ascii(f_mag, 'mag')

    for v in ['time'] + s_vars:
        swe[v] = np.append(swe[v], swe_now[v])
    for v in ['time'] + m_vars:
        mag[v] = np.append(mag[v], mag_now[v])

# Remove bad data points:
for v in s_vars:
    swe[v] = pair(swe['time'], swe[v], swe['time'], varname=v)
for v in m_vars:
    mag[v] = pair(mag['time'], mag[v], mag['time'], varname=v)

# Convert into a nice IMF input object:
imfout = ImfInput(args.outfile, load=False, npoints=mag['time'].size)
imfout['time'] = swe['time']
for v in s_vars:
    imfout[v] = swe[v]
for v in m_vars:
    imfout[v] = mag[v]
imfout['v'] = -1 * swe['ux']

if args.propagate:
    l1_propagate(imfout, smoothwin=args.smoothing,
                 outfile=args.outfile[:-4] + '_propagated.dat')
imfout.write()