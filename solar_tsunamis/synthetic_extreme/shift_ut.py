#!/usr/bin/env python3

'''
Given an input IMF file and number of hours, time shift the event and
associated start/end times to create a new UT for the storm onset.

The epoch of interest is the storm start time, not the start of the file.
The file is shifted so that the storm onset occurs at the set hour/season
specified by the user. Note that the time between the start of the input
IMF file and the storm onset is assumed to be 8.3 hours, but can be changed
via optional argument.

The start and end times of the simulation are printed to screen and, if
an input PARAM shared, the PARAM updated to match these updated times.
Times are set with a given amount of preconditioning time (time before the
storm onset, defaulting to 4 hours).

If #IDEALAXES is found in the PARAM file, it is removed.

If the `--season` argument is used, the start time can be drastically shifted
to capture different seasons (reference: northern hemisphere). Possible
values shown below:

Value    | Start Date
---------|---------------------------
winter   | 2000/12/21 (default value)
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
parser.add_argument("-onset", "--onset", type=float, default=8.30,
                    help='Set the hours-from-file-start of the storm onset.')
parser.add_argument("-tp", "--precond", type=float, default=4.0,
                    help="Set the preconditioning time (simulation start to " +
                    "storm onset) in hours.")
parser.add_argument("-d", "--duration", type=int, default=32,
                    help='Set the simulation duration in hours.')
parser.add_argument("file", type=str,
                    help='The SWMF solar wind input file to rotate in time.')
parser.add_argument('--season', '-s', type=str, default='winter',
                    help='Set northern hemisphere season.')
parser.add_argument("-v", "--viz", action='store_true', default=False,
                    help="Visualize propagation using matplotlib.")
parser.add_argument("-p", "--param", type=str, default=None,
                    help="Name of PARAM input file to update with UT shift.")
args = parser.parse_args()

# Quick check:
print(f"Rotating start time by {args.hours} hours.")
print(f"Shifting season to {args.season}")

# Get DEFAULT STORM ONSET TIMES based on season:
starts = {'summer': dt.datetime(2000, 6, 21, 0, 0, 0),
          'winter': dt.datetime(2000, 12, 21, 0, 0, 0),
          'equinox': dt.datetime(2000, 3, 20, 0, 0, 0)}

# Get the desired UT for storm onset:
target_onset = starts[args.season] + dt.timedelta(hours=args.hours)

# Check season:
if args.season not in list(starts.keys()):
    raise ValueError('Invalid season.')

# Set updated start and end time for the simulation.
# These values are for the params.
param_start = target_onset - dt.timedelta(hours=args.precond)
param_end = param_start + dt.timedelta(hours=args.duration)

# Open IMF file:
imf = ImfInput(args.file)

# Obtain the shift between the desired onset and the onset of the file.
file_onset = imf['time'][0] + dt.timedelta(hours=args.onset)
timedelta = file_onset - target_onset
t_shifted = imf['time'] - timedelta  # FINAL TIMESHIFTED TIMESERIES.

# Set file name:
new_name = imf.attrs['file'][:-4] + f'_{args.season}_{args.hours:02d}UT.dat'

time_commands = []
for t, cmd in zip((param_start, param_end), ('#STARTTIME', '#ENDTIME')):
    time_commands.append(f'''{cmd}
{t.year:04d}                      iYear
{t.month:02d}                        iMonth
{t.day:02d}                        iDay
{t.hour:02d}                        iHour
{t.minute:02d}                        iMinute
{t.second:02d}                        iSecond
0.0                       FracSecond
''')

# Print info to screen:
print('NEW TIME COMMANDS:')
for cmd in time_commands:
    print(cmd)
print(f'New file name:\n{new_name}')

# Alter PARAM:
if args.param:
    # Get old param:
    with open(args.param, 'r') as f:
        lines = f.readlines()

    # Remove IDEALAXES:
    if '#IDEALAXES\n' in lines:
        print('Removing IDEALAXES from PARAM...')
        lines.remove('#IDEALAXES\n')

    # Replace IMF input line:
    lines[lines.index('#SOLARWINDFILE\n') + 2] = f"{new_name}\n"

    # Replace Start and End times:
    istart, iend = lines.index('#STARTTIME\n'), lines.index('#ENDTIME\n')
    lines[istart] = time_commands[0]
    lines[iend] = time_commands[1]

    # Remove old time command pieces:
    for i in range(7):
        lines.pop(iend + 1)
    for i in range(7):
        lines.pop(istart + 1)

    # Write to new param file:
    outparam = args.param + "_shifted"
    with open(outparam, 'w') as out:
        for l in lines:
            out.write(l)

# If vizualizing, viz!
if args.viz:
    fig1 = imf.quicklook(title="Original Data")
    imf['time'] = t_shifted
    fig2 = imf.quicklook(title=f"New Storm Onset: {target_onset}")
    if not plt.isinteractive():
        plt.show()

# Write out to file.
imf.attrs['file'] = new_name
imf['time'] = t_shifted
imf.write()

