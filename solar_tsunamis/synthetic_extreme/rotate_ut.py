#!/usr/bin/env python3

'''
Given an input IMF file and number of hours, "rotate" the event and
associated start/end times to create a UT offset.
'''

import datetime as dt
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from spacepy.plot import style
from spacepy.pybats import ImfInput

style()

# Start by configuring the argparser:
parser = ArgumentParser(description=__doc__,
                        formatter_class=RawDescriptionHelpFormatter)
parser.add_argument("hours", type=int, help="Number of hours to rotate.")
parser.add_argument("file", type=str,
                    help='The SWMF solar wind input file to rotate in time.')
parser.add_argument("-v", "--viz", action='store_true', default=False,
                    help="Visualize propagation using matplotlib.")
args = parser.parse_args()

# Get offset:
t_shift = dt.timedelta(hours=args.hours)

# Set updated start and end time:
t_start = dt.datetime(2000, 1, 1, 4, 0, 0) + t_shift
t_end = dt.datetime(2000, 1, 2, 12, 2, 0) + t_shift

# Open IMF file:
imf = ImfInput(args.file)

# Shift time, print updated args to screen.
t_new = imf['time'] + t_shift

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
    fig = imf.quicklook()
    for v, ax in zip(plotvars, fig.axes):
        col = ax.lines[0].get_color()
        ax.plot(t_new, imf[v], '--', c=col)

# Write out to file.
imf.attrs['file'] = imf.attrs['file'][:-4] + f'_shift{args.hours:02d}.dat'
imf['time'] = t_new
imf.write()
