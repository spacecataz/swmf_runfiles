#!/usr/bin/env python

'''
Develop interpolation stuff.
'''

import os
import datetime as dt

import numpy as np
from scipy.interpolate import LinearNDInterpolator as linterp
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from spacepy import coordinates as crds
from spacepy.time import Ticktock

# Set input and output files/directories:
infile = 'dec2021eclipse/combined_parms_2dall_base.npz'
outdir = 'CondFies_Dec2021_Base/'
if not os.path.exists(outdir):
    os.mkdir(outdir)

# Load the data, create helper variables.
gitm = np.load(infile)
psi = np.pi*gitm['glon']/180. + np.pi/2  # polar angle.

# Set start time for simulation:
start_time = dt.datetime(2021, 12, 4, 0, 0, 0)

itime = 0

# Extract values from GitM, wrap lat/lon to create extended grid.
gitlat, gitlon = gitm['glat'], gitm['glon']

# Get sizes of resulting arrays:
nlats, nlons = gitlat.size, gitlon.size

# Create time array using TickTock
tnow = Ticktock(nlons * [start_time + dt.timedelta(hours=gitm['ut'][itime])])
# ticks = Ticktock(npts * [tnow])
glat = np.zeros([nlons, nlats])
glon = np.zeros([nlons, nlats])
mlat = np.zeros([nlons, nlats])
mlon = np.zeros([nlons, nlats])

timing_start = dt.datetime.now()

# Loop over slices of constant geo latitude:
for i in range(nlats):
    # Fold into 2D array.
    glat[:, i], glon[:, i] = nlons*[gitlat[i]], gitlon

    # Convert to SM coords:
    pts = np.array([nlons*[1], glat[:, i].flatten(),
                    glon[:, i].flatten()]).transpose()
    gm_coord = crds.Coords(pts, dtype='GEO', carsph='sph', ticks=tnow)
    sm_coord = gm_coord.convert('SM', 'sph')
    mlat[:, i], mlon[:, i] = sm_coord.lati, sm_coord.long + 180

# Extract conductance:
sigH, sigP = gitm['SigH'][itime, :, :], gitm['SigP'][itime, :, :]

print("Timing to rotate grid: ",
      (dt.datetime.now() - timing_start).total_seconds())
timing_start = dt.datetime.now()

# Create interpolator
points = list(zip(mlon.flatten()-365, mlat.flatten())) + \
         list(zip(mlon.flatten(), mlat.flatten())) + \
         list(zip(mlon.flatten()+365, mlat.flatten()))

intsigh = linterp(points, 3*list(sigH.flatten()), fill_value=0)
intsigp = linterp(points, 3*list(sigP.flatten()), fill_value=0)

print("Timing to create interpolators: ",
      (dt.datetime.now() - timing_start).total_seconds())

fig, ax = plt.subplots(1, 1, figsize=(10, 7))
patch = Rectangle((0, -90), 360, 180, ec='k', fill=False)
pts1 = ax.plot(glon, glat, 'ok', ms=.3, label='GEO Coords')
pts2 = ax.plot(mlon, mlat, '.r', ms=.5, label='SM Coords')
ax.add_patch(patch)

ax.set_title('GITM Output Points', size=20, loc='left')
ax.set_xlabel('Longitude', size=16)
ax.set_ylabel('Latitude', size=16)
fig.legend([pts1[0], pts2[0]], ['GEO Coords', 'SM Coords'],
           ncol=2, fontsize=16)
fig.tight_layout()

# Re-create IE grid exactly:
rim_nlat, rim_nlon = 91, 181
dlat, dlon = 90./(rim_nlat-1), 360./(rim_nlon-1)
rim_lon, rim_lat = np.meshgrid(np.arange(0, 360+dlon, dlon),
                               np.arange(0, 90+dlat, dlat))
# rim_lon = np.arange(0, 360+dlon, dlon)
# rim_lat = np.arange(0, 90+dlat, dlat)
# ax.plot(rim_lon, rim_lat, '.c', ms=.5)

rim_sighN = intsigh(list(zip(rim_lon.flatten(), rim_lat.flatten()))).reshape([91, 181])
rim_sighS = intsigh(list(zip(rim_lon.flatten(), -rim_lat.flatten()))).reshape([91, 181])

fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 8))
a1.contourf(rim_lon, rim_lat, rim_sighN)
a1.contourf(rim_lon, -1*rim_lat, rim_sighS)
a2.tricontourf(mlon.flatten(), mlat.flatten(), sigH.flatten())
