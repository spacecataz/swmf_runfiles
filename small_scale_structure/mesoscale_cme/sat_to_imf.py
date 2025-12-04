#!/usr/bin/env python3

'''
Convert a heliospheric virtual satellite to a magnetospheric solar wind
and IMF input file.

This script assumes the units and configuration as provided by Dr. Manchester,
Dec., 2025.
'''

from spacepy.pybats import ImfInput
from spacepy.pybats.bats import VirtSat

from argparse import ArgumentParser, RawDescriptionHelpFormatter


# Start by configuring the argparser:
parser = ArgumentParser(description=__doc__,
                        formatter_class=RawDescriptionHelpFormatter)
parser.add_argument("satfile", type=str,
                    help='The input satellite extraction.')
parser.add_argument('-c', '--coords', type=str, default='GSE',
                    help='Set the coordinate system used by the input file.')
args = parser.parse_args()


# Constants:
mp = 1.67262192e-24   # in grams.
boltz = 1.380649e-23  # in m2 * kg /s**2 / K (SI units)
g_to_nt = 1.E5        # cgs to nT
p_to_t = 1 / (1e7 * boltz)  # cgs pressure to Kelvin

# Open satellite file, grab key info:
sat = VirtSat(args.satfile)
sat.calc_temp(units='K')
npoints = sat['time'].size

# Create empty IMF object:
imf = ImfInput(filename='imf_'+args.satfile, load=False, npoints=npoints)

# Set coordinates and comments:
imf.attrs['coor'] = args.coords
imf.attrs['header'].append(f'Converted from {args.satfile}\n')

# Fill and write.
# Copy over variables that map name-to-name:
for v in ['time', 'ux', 'uy', 'uz', 'bx', 'by', 'bz']:
    imf[v] = sat[v]
    if 'b' in v:
        imf[v] *= g_to_nt
# Density is special.
imf['n'] = sat['rho']/mp
# Temperature is special.
imf['t'] = sat['p']/imf['n'] * p_to_t

# Set Earthward velocity:
imf['v'] = -imf['ux']

# Write to file:
imf.write()

