#!/usr/bin/env python

'''
Using GITM outputs, create a set of input files to be read by Ridley_serial
and used during SWMF simulations.

There are also tools to plot the input files for inspection and debugging.
'''

import os
import datetime as dt

import numpy as np
from scipy.interpolate import LinearNDInterpolator as linterp
import matplotlib.pyplot as plt

from spacepy import coordinates as crds
from spacepy.time import Ticktock

# Set input and output files/directories:
infile = 'dec2021eclipse/combined_parms_2dall_euv.npz'
outdir = 'CondFies_Dec2021_EUV/'
if not os.path.exists(outdir):
    os.mkdir(outdir)

# Set start time for simulation:
start_time = dt.datetime(2021, 12, 4, 0, 0, 0)

# Load the data, create helper variables.
gitm = np.load(infile)
psi = np.pi*gitm['glon']/180. + np.pi/2  # azimuthal angle.

# Mask cond if it exists:
if 'SolarMask' in gitm:
    gitm_sigp = gitm['SigP'] * gitm['SolarMask']
    gitm_sigh = gitm['SigH'] * gitm['SolarMask']
else:
    gitm_sigp = gitm['SigP']
    gitm_sigh = gitm['SigH']

# Extract values from GITM, wrap lat/lon to create extended grid.
glat, glon = np.meshgrid(gitm['glat'], gitm['glon'])
nlats, nlons = gitm['glat'].size, gitm['glon'].size

# Re-create IE grid exactly:
rim_nlat, rim_nlon = 91, 181
dlat, dlon = 90./(rim_nlat-1), 360./(rim_nlon-1)
rim_lon, rim_lat = np.meshgrid(np.arange(0, 360+dlon, dlon),
                               np.arange(0, 90+dlat, dlat))
flat_lon, flat_lat = rim_lon.flatten(), rim_lat.flatten()

# Create points, note that we need colat-ordering so
# flip points in northern hemisphere..
rim_ptsN = list(zip(flat_lon, 90 - flat_lat))
rim_ptsS = list(zip(flat_lon, -flat_lat))
rim_psi = np.pi*rim_lon/180. - np.pi/2


def write_cond_rim(itime, hallN, hallS, pedN, pedS):
    '''
    Write conductance files for time=*itime* to file.
    '''
    tnow = start_time + dt.timedelta(hours=gitm['ut'][itime])

    file_N = outdir + f'cond_N_t{tnow:%Y%m%d_%H%M%S}.dat'
    file_S = outdir + f'cond_S_t{tnow:%Y%m%d_%H%M%S}.dat'

    # Flatten our hall/pedersen arrays for convenience.
    hn, hs = hallN.flatten(), hallS.flatten()
    pn, ps = pedN.flatten(), pedS.flatten()

    with open(file_N, 'w') as outN, open(file_S, 'w') as outS:
        # Write headers:
        outN.write(f'T = {tnow}\n')
        outS.write(f'T = {tnow}\n')
        outN.write('mlon\tmlat\tsigma_Hall\tsigma_Peder\n')
        outS.write('mlon\tmlat\tsigma_Hall\tsigma_Peder\n')

        # Write away:
        for i, (lon, lat) in enumerate(rim_ptsN):
            outN.write(f"{lon:07.3f} {lat:07.3f} "
                       + f"{hn[i]:012.8f} {pn[i]:012.8f}")
            outS.write(f"{lon:07.3f} {lat:07.3f} "
                       + f"{hs[i]:012.8f} {ps[i]:012.8f}")
            outN.write("\n")
            outS.write("\n")


def interp_to_rim(itime, mincond=0.5, dosave=True, doplot=True):
    '''
    Using the information about RIM's grid (in SM coords) and the GITM
    results (in geographic coords), interpolate from GITM to RIM.

    Create comparison plots and save to file if **doplot** is True.

    If **dosave** is True, save results to an ascii file.

    Four arrays are returned: sighN, sighS, sigpN, and sigpS representing
    Hall & Pedersen conductances in both the north and south hemisphere.
    '''

    # Create some arrays for storage:
    mlat = np.zeros([nlons, nlats])
    mlon = np.zeros([nlons, nlats])

    # Extract conductance from file.
    sigH, sigP = gitm_sigh[itime, :, :], gitm_sigp[itime, :, :]

    # Create time array using TickTock
    tnow = Ticktock(nlons * [start_time +
                             dt.timedelta(hours=gitm['ut'][itime])])

    # Loop over slices of constant geo latitude:
    for i in range(nlats):
        # Flatten lat/lon pairs; convert to SM coords
        pts = np.array([nlons*[1], glat[:, i].flatten(),
                        glon[:, i].flatten()]).transpose()
        gm_coord = crds.Coords(pts, dtype='GEO', carsph='sph', ticks=tnow)
        sm_coord = gm_coord.convert('SM', 'sph')

        # Stash result into SM arrays:
        mlat[:, i], mlon[:, i] = sm_coord.lati, sm_coord.long # + 180

    # Create interpolator. Copy 3x to ensure continuity over Lon = 0/360.
    points = list(zip(mlon.flatten()-365, mlat.flatten())) + \
        list(zip(mlon.flatten(), mlat.flatten())) + \
        list(zip(mlon.flatten()+365, mlat.flatten()))

    intsigh = linterp(points, 3*list(sigH.flatten()), fill_value=sigH.min())
    intsigp = linterp(points, 3*list(sigP.flatten()), fill_value=sigP.min())

    # Now interpolate onto new grid:
    rim_sighN = intsigh(rim_ptsN).reshape([91, 181])
    rim_sighS = intsigh(rim_ptsS).reshape([91, 181])
    rim_sigpN = intsigp(rim_ptsN).reshape([91, 181])
    rim_sigpS = intsigp(rim_ptsS).reshape([91, 181])

    # Save to file:
    if dosave:
        write_cond_rim(itime, rim_sighN, rim_sighS, rim_sigpN, rim_sigpS)

    # Only stick around if we're going to make a plot.
    if not doplot:
        return rim_sighN, rim_sighS, rim_sigpN, rim_sigpS

    t = tnow[0].data[0]
    kwargs = {'vmin': 0, 'vmax': 25, 'extend': 'both',
              'levels': np.arange(0, 25.5, 0.5)}

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 8))
    c1 = a1.contourf(rim_lon, 90-rim_lat, rim_sighN, **kwargs)
    c2 = a1.contourf(rim_lon, -1*rim_lat, rim_sighS, **kwargs)
    c2 = a2.tricontourf(mlon.flatten(), mlat.flatten(), sigH.flatten(),
                        **kwargs)

    a1.set_title('Interpolated Conductace: Hall')
    a2.set_title('Rotated GITM Conductance: Hall')
    for a, c in zip([a1, a2], [c1, c2]):
        a.set_xlabel(r'SM Lon ($^{\circ}$)')
        a.set_ylabel(r'SM Lat ($^{\circ}$)')
        plt.colorbar(c, ax=a, label='Hall Cond. ($Siemens$)')
    fig.suptitle(f'T={t}')
    fig.tight_layout()
    fig.savefig(outdir + f'interp_H_t{t:%Y%m%d_%H%M%S}.png')

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 8))
    c1 = a1.contourf(rim_lon, 90-rim_lat, rim_sighN, **kwargs)
    c2 = a1.contourf(rim_lon, -1*rim_lat, rim_sighS, **kwargs)
    c2 = a2.tricontourf(mlon.flatten(), mlat.flatten(), sigH.flatten(),
                        **kwargs)

    a1.set_title('Interpolated Conductace: Pedersen')
    a2.set_title('Rotated GITM Conductance: Pedersen')
    for a, c in zip([a1, a2], [c1, c2]):
        a.set_xlabel(r'SM Lon ($^{\circ}$)')
        a.set_ylabel(r'SM Lat ($^{\circ}$)')
        plt.colorbar(c, ax=a, label='Ped. Cond. ($Siemens$)')
    fig.suptitle(f'T={t}')
    fig.tight_layout()
    fig.savefig(outdir + f'interp_P_t{t:%Y%m%d_%H%M%S}.png')

    # Set minimum values:
    for cond in (rim_sighN, rim_sighS, rim_sigpN, rim_sigpS):
        cond[cond < mincond] = mincond

    # Return conductance:
    return rim_sighN, rim_sighS, rim_sigpN, rim_sigpS


def plot_rim_sigma(itime, hallN, hallS, pedN, pedS, maxz=20, latlim=45,
                   nlevs=50, dosave=True, polar=True):
    '''
    Create plot of RIM conductance.
    '''
    fig, axes = plt.subplots(2, 2, figsize=(8, 8),
                             subplot_kw={'polar': polar})
    fig.subplots_adjust(left=0.06, bottom=0.133, right=.955, top=.905,
                        hspace=0.35, wspace=0.25)
    x = rim_psi[0, :] if polar else rim_lon[0, :]
    yN = rim_lat[:, 0] if polar else rim_lat[:, 0]

    # Set levels and contour kwargs.
    levs = np.linspace(0, maxz, nlevs)
    kwargs = {'levels': levs, 'extend': 'max'}

    # Northern Hemisphere:
    loc = rim_lat[:, 0] > latlim
    z = hallN[loc, :]
    cont = axes[0, 0].contourf(x, yN[loc], z, **kwargs)
    axes[0, 0].set_title(r'North $\Sigma_{Hall}$')

    z = pedN[loc, :]
    axes[0, 1].contourf(x, yN[loc], z, **kwargs)
    axes[0, 1].set_title(r'North $\Sigma_{Ped}$')

    # Southern Hemisphere:
    loc = -rim_lat[:, 0] < -latlim
    z = hallS[loc, :]
    axes[1, 0].contourf(x, -rim_lat[:, 0][loc], z, **kwargs)
    axes[1, 0].set_title(r'South $\Sigma_{Hall}$')

    z = pedS[loc, :]
    axes[1, 1].contourf(x, -rim_lat[:, 0][loc], z, **kwargs)
    axes[1, 1].set_title(r'South $\Sigma_{Ped}$')

    tnow = start_time + dt.timedelta(hours=gitm['ut'][itime])
    fig.suptitle(f"T={tnow}")

    # Add a color bar.
    fig.colorbar(cax=fig.add_axes([0.15, .07, .7, .02]), mappable=cont,
                 label=r'RIM Conductance ($Siemens$)',
                 orientation='horizontal')

    if dosave:
        fig.savefig(outdir + f"rim_cond_T{tnow:%Y%m%d_%H%M%S}.png")


def plot_gitm_sigma(itime, maxz=20, latlim=45, nlevs=50, dosave=True,
                    polar=True):
    '''
    For time iteration *itime*, plot both the Hall and Pedersen conductance
    in geographic coordinates.
    '''

    fig, axes = plt.subplots(2, 2, figsize=(8, 8),
                             subplot_kw={'polar': polar})
    fig.subplots_adjust(left=0.06, bottom=0.133, right=.955, top=.905,
                        hspace=0.35, wspace=0.25)
    x = psi if polar else gitm['glon']
    yN = 90 - gitm['glat'] if polar else gitm['glat']

    # Set levels and contour kwargs.
    levs = np.linspace(0, maxz, nlevs)
    kwargs = {'levels': levs, 'extend': 'max'}

    # Northern Hemisphere:
    loc = gitm['glat'] > latlim
    z = gitm_sigh[itime, :, loc]
    cont = axes[0, 0].contourf(x, yN[loc], z, **kwargs)
    axes[0, 0].set_title(r'North $\Sigma_{Hall}$')

    z = gitm_sigp[itime, :, loc]
    axes[0, 1].contourf(x, yN[loc], z, **kwargs)
    axes[0, 1].set_title(r'North $\Sigma_{Ped}$')

    # Southern Hemisphere:
    loc = gitm['glat'] < -latlim
    z = gitm_sigh[itime, :, loc]
    axes[1, 0].contourf(x, gitm['glat'][loc], z, **kwargs)
    axes[1, 0].set_title(r'South $\Sigma_{Hall}$')

    z = gitm_sigp[itime, :, loc]
    axes[1, 1].contourf(x, gitm['glat'][loc], z, **kwargs)
    axes[1, 1].set_title(r'South $\Sigma_{Ped}$')

    tnow = start_time + dt.timedelta(hours=gitm['ut'][itime])
    fig.suptitle(f"T={tnow}")

    # Add a color bar.
    fig.colorbar(cax=fig.add_axes([0.15, .07, .7, .02]), mappable=cont,
                 label=r'GITM Conductance ($Siemens$)',
                 orientation='horizontal')

    if dosave:
        fig.savefig(outdir + f"gitm_cond_T{tnow:%Y%m%d_%H%M%S}.png")


def create_cond():
    '''
    For the case given by *infile* and *outdir*, produce all plots and
    conductance files.
    '''

    set_inter = True if plt.isinteractive() else False
    plt.ioff()

    for itime in range(gitm['ut'].shape[0]):
        print(f"Working on iTime = {itime}")
        hallN, hallS, pedN, pedS = interp_to_rim(itime)
        plot_rim_sigma(itime, hallN, hallS, pedN, pedS)
        plot_gitm_sigma(itime)
        plt.close('all')

    if set_inter:
        plt.ion()
