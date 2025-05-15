#!/usr/bin/env python3
'''
Vis our source term.
'''
from glob import glob

import numpy as np
import matplotlib.pyplot as plt

from spacepy.pybats import bats


plt.style.use('fivethirtyeight')


#  Physical Constants.
re = 6378000  # Earth radii in meters.
mp = 1.67262192E-27  # proton mass.


def gauss(x, rspread=1):
    gauss = (1/np.sqrt(2*rspread*np.pi)) * np.exp(-x**2/(2*rspread**2))
    return gauss


def plot_gaussian(rspread=1):
    '''Plot a guassian for fun and profit.'''
    dist = np.linspace(-5, 5, 500)
    plt.plot(dist, gauss(dist))


def estimate_source(A=100, rspread=1, dx=0.5, npts=5):
    '''
    Estimate the source rate (#/s and kg/s) of a spacecraft of source rate
    A (in protons per cubic centimeter per second) with a Gaussian spread of
    `rspread` and grid size of `dx`.
    '''

    # Units! Constants!
    vol = dx**3
    A *= 1E6 * re**3  # protons/s/cm^3 to protons/s/RE^3

    rate = 0
    # Do a npts x npts grid:
    half = (npts-1) // 2
    for i in range(-half, half+1):
        for j in range(-half, half+1):
            d = np.sqrt(i**2 + j**2)
            g = gauss(d, rspread=rspread)
            # print(f"i, j = {i}, {j} -- d, gauss = {d:.3f}, {g:.3f}")
            rate += g * A * vol

    return rate, rate*mp


def estimate_bw_rec(A=132.55, dx=0.25, rspread=0.25, nsat=4):
    '''
    A convenience function for calculating the values required to
    achieve BW's recommendation of 124,100kg of mass over 12 hours.
    '''

    target = 124100 / (12*3600.)
    print(f"Target value is {target:.5f}kg/s")
    print(f"...or {target/nsat:.5f} per S/C")

    print(f"Using A={A}, rspread={rspread}, and dx={dx}...")
    rate, massrate = estimate_source(A, dx=dx, npts=15, rspread=rspread)
    print(f"...we achieve a per-spacecraft outflow rate of {massrate:.5f}")

def integrate_dens(mhd, res):
    '''
    Given a 3D file of *uniform* grid spacing, integrate mass density into
    total number of protons in the system.

    Parameters
    ----------
    mhd : IdlFile
        A 3d file read in as a PyBats IdlFile object.

    res : float
        The grid spacing in the `mhd` file.

    Returns
    -------
    protons : int
        Total number of protons in the system.
    mass : float
        Total mass in the system.
    '''

    # Volume of a single cell, in cm^3
    vol = (res * re * 100)**3

    # Integrate:
    protons = 0.0
    for rho in mhd['rho']:
        protons += rho * vol

    return protons, protons*mp


def get_mass(res, s='GM/IO2/'):
    '''
    Find all files in the PWD, calculate total particles/mass, and
    return as a function of time.
    '''

    files = glob(s + '3d*.out')

    nfiles = len(files)
    time, num, mass = np.zeros(nfiles), np.zeros(nfiles), np.zeros(nfiles)

    for i, f in enumerate(files):
        mhd = bats.IdlFile(f, keep_case=False)
        time[i] = mhd.attrs['runtime']
        num[i], mass[i] = integrate_dens(mhd, res)

    return time, num, mass


def plot_mass_change(res, s='GM/IO2/'):
    '''
    Given a test run, integrate and plot the change in mass and number
    density.
    '''

    time, num, mass = get_mass(res, s=s)

    dnum, dmass = num-num[0], mass-mass[0]

    fig, (a1, a2) = plt.subplots(2, 1)

    a1.plot(time, dnum)
    a2.plot(time, dmass)
    a1.set_ylabel(r'$\Delta N$ ($protons$)')
    a2.set_ylabel(r'$\Delta m$ ($kg$)')
    a2.set_xlabel('Run time ($s$)')
    fig.tight_layout()


def plot_mass_dens_2d(s='GM/IO2/'):
    '''Plot all z=0 density slices.'''
    files = glob(s + 'z*.out')

    kwargs = {'add_cbar': True, 'zlim': [0.01, 10.], 'dolog': True}

    for i, f in enumerate(files[1:]):
        mhd = bats.Bats2d(f)
        fig, ax, cnt, cbar = mhd.add_contour('x', 'y', 'rho', **kwargs)
        ax.set_title(f'T={mhd.attrs["runtime"]:.2f}s')
