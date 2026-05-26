#!/usr/bin/env python3

'''
Given an input IMF file and number of hours, "rotate" the event and
associated start/end times to create a UT offset.

If the `--season` argument is used, the start time can be drastically shifted
to capture different seasons (reference: northern hemisphere). Possible
values shown below:

Value    | Start Date
---------|---------------------------
winter   | 2000/01/01 (default value)
equinox  | 2000/03/20
summer   | 2000/06/21

Example: Use a 3 hour offset using northern hemisphere summer:
>>> rotate_ut.py 3 imf_input_files/imf_G1000_KatusMedian.dat --season summer

'''

import datetime as dt
from argparse import ArgumentParser, RawDescriptionHelpFormatter

import matplotlib.pyplot as plt
from spacepy.plot import style
from spacepy.pybats import ImfInput

style()

# Start by configuring the argparser:
parser = ArgumentParser(description=__doc__,
                        formatter_class=RawDescriptionHelpFormatter)
parser.add_argument("hours", type=int, help="Number of hours to rotate.")
parser.add_argument("file", type=str,
                    help='The SWMF solar wind input file to rotate in time.')
parser.add_argument('--season', '-s', type=str, default='winter',
                    help='Set northern hemisphere season.')
parser.add_argument("-v", "--viz", action='store_true', default=False,
                    help="Visualize propagation using matplotlib.")
args = parser.parse_args()

# Quick check:
print(f"Rotating start time by {args.hours} hours.")
print(f"Shifting season to {args.season}")

# Get offset:
t_shift = dt.timedelta(hours=args.hours)

# Get start time based on season:
starts = {'summer': dt.datetime(2000, 6, 21, 4, 0, 0),
          'winter': dt.datetime(2000, 1, 1, 4, 0, 0),
          'equinox': dt.datetime(2000, 3, 20, 4, 0, 0)}

# Check season:
if args.season not in list(starts.keys()):
    raise ValueError('Invalid season.')

# Set updated start and end time:
t_start = starts[args.season] + t_shift
t_end = starts[args.season] + dt.timedelta(hours=32) + t_shift

# Open IMF file:
imf = ImfInput(args.file)

# Shift time, print updated args to screen.
timedelta = imf['time'] - imf['time'][0]
t_season = t_start + timedelta
t_new = t_start + timedelta + t_shift

for t, cmd in zip((t_start, t_end), ('#STARTTIME', '#ENDTIME')):
    print(f'''
{cmd}
{t.year:04d}                      iYear
{t.month:02d}                        iMonth
{t.day:02d}                        iDay
{t.hour:02d}                        iHour
{t.minute:02d}                        iMinute
{t.second:02d}                        iSecond
0.0                       FracSecond
''')

# If vizualizing, viz!
if args.viz:
    plotvars = ['by', 'bz', 'n', 'v']
    imf['time'] = t_season
    fig = imf.quicklook()
    for v, ax in zip(plotvars, fig.axes):
        col = ax.lines[0].get_color()
        ax.plot(t_new, imf[v], '--', c=col)
    if not plt.isinteractive():
        plt.show()

# Write out to file.
imf.attrs['file'] = imf.attrs['file'][:-4] + \
    f'_shift{args.hours:02d}_{args.season}.dat'
imf['time'] = t_new
imf.write()

print(f'New file name:\n{imf.attrs["file"]}')
