#!/usr/bin/env python3
'''
Vis our source term.
'''
from glob import glob

import numpy as np
import matplotlib.pyplot as plt

from spacepy.pybats import bats, parse_filename_time

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
    vol = (res * re * 1000)**3

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
