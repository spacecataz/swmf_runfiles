#!/usr/bin/env python3
'''
Create estimates for Gopalswamy storms
'''

from glob import glob

import numpy as np
from scipy.io import loadmat
import matplotlib.pyplot as plt

plt.style.use('fivethirtyeight')

# Set some constants:
v_a, v_gam, v_eta = 3.5, 3.35379, 0.5  # Velocity coefficients
e_a, e_gam, e_eta = 3.1, 32.7, 1.9     # Energy coefficients

# Characteristics of Katus event:
vmax_mean, vmax_medi = 639.39, 612.6
nmax_mean, nmax_medi = 22.05, 20.24
bmax_mean, bmax_medi = 15.701152823917102, 15.028552824540359

# Gopalswamy estimates for energy/velocity for 1/100 and 1/1000 year storm:
e100, e1000 = 4.4E33, 9.8E33
v100, v1000 = 3800, 4670


def v_to_b(v):
    '''Given a solar wind velocity (km/s), return TOTAL magnetic field in nT'''
    return 0.06*v - 13.58


def weibull(x, a=v_a, gamma=v_gam, eta=v_eta, m=1.0):
    '''
    For input `x`, return the corresponding `y` value using a Weibull
    distribution. Kwargs are Weibull parameters.

    This function is based on the Gopalswamy work; it returns occurrence
    (#/year).
    '''

    X = np.log10(x)
    A1 = (gamma-X)/eta
    Y = a * (1-np.exp(-(A1)**m))

    return 10**Y


def inv_weib(y, a=v_a, gamma=v_gam, eta=v_eta, m=1.0):
    '''
    Given a value, `y`, return the corresponding `x` as calculated using
    the inverse of the Weibull function. All parameters are Weibull params.
    '''

    Y = np.log10(y)
    X = eta * np.log(1 - Y/a) + gamma

    return 10**X


def plot_gopal_distros():
    '''
    Reproduce the Gopalswamy distribution plots.
    '''

    dv = 10
    v = np.arange(100, 4700+dv, dv)
    e = 10**np.arange(27.5, 34, .01)

    fig, (a1, a2) = plt.subplots(1, 2)

    a1.loglog(v, weibull(v))
    a1.set_xlabel('Velocity ($km/s$)')
    a1.set_ylabel('Occurrence ($\#/year$)')

    ymin, ymax = a1.get_ylim()
    #a1.vlines(vmax_mean, ymin, ymax, line)

    a2.loglog(e, weibull(e, a=e_a, eta=e_eta, gamma=e_gam))
    a2.set_xlabel('Energy ($erg$)')
    a2.set_ylabel('Occurrence ($\#/year$)')

    fig.tight_layout()


def v_plaw(years):
    '''
    Given an occurrence of 1/Y years, determine the approximate CME
    speed using the Gopalswamy powerlaw fitting.
    '''
    pass


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


def analyze_katusdens(category='SH'):
    '''
    Use the Katus et al. data to search for possible relationships between
    event energy and maximum density.

    Parameters
    ----------
    category : str, defaults to "SH"
        Set storm category: CME, SH, MC
    '''

    print("Enter location of raw data (e.g., " +
          "/users/uname/SEAdata/), enter X to exit")
    data_dir = '/home/dwelling/projects/SEA_drivers/Dan_SEA_2023v1/'
    # data_dir = input() + '/'
    if data_dir[0] == 'X':
        exit()

    # Open data:
    dens = loadmat(data_dir + f'{category}/RawSEAdata/Nn.mat')['Data']
    vels = loadmat(data_dir + f'{category}/RawSEAdata/Nv.mat')['Data']

    # Remove nans:
    dens[np.isnan(dens)] = 0
    vels[np.isnan(vels)] = 0

    # Get max vals:
    max_n = dens.max(axis=0)
    max_v = vels.max(axis=0)

    loc_big = max_v > 750.

    # Get occurrence, convert to energy
    occur = weibull(max_v)
    ener = inv_weib(occur, a=e_a, eta=e_eta, gamma=e_gam)

    # Make some pretty plots.
    fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(8, 4))
    fig.suptitle(f'CME Characteristic Relationships ({category}-type)')
    a1.plot(max_v, max_n, '*')
    a1.plot(max_v[loc_big], max_n[loc_big], '*')
    a1.set_xlabel('Max $V$ ($km/s$)')
    a1.set_ylabel('Max $n$ ($cm^{-3}$)')
    a2.plot(max_v, ener, '*')
    a2.set_xlabel('Max $V$ ($km/s$)')
    a2.set_ylabel('Energy ($ergs$)')
    a3.plot(ener, max_n, '*')
    a3.plot(ener[loc_big], max_n[loc_big], '*')
    a3.set_xlabel('Energy ($ergs$)')
    a3.set_ylabel('Max $n$ ($cm^{-3}$)')
    fig.tight_layout()


def scale_dens(v_in, n_in, volrat=1, debug=False):
    '''
    Convert Katus et al max velocity and density into extreme storm densities
    for the 1/100 and 1/1000 year storms.

    Parameters
    ----------
    v_in, n_in : float
        Velocity and density to scale for extreme event.
    volrat : float, defaults to 1
        Set the velocity ratio of the extreme event to the regular one.
    '''

    # Get the occurrence of storm, then obtain the energy in ergs.
    occ = weibull(v_in)
    ener = inv_weib(occ, a=e_a, eta=e_eta, gamma=e_gam)

    if debug:
        print(f'For a storm of velocity {v_in}, occurrence is {occ:.1f} ' +
              'events/year and energy is {ener:.2E} ergs')

    # Get scaling factor:
    gamma100 = e100/ener / volrat
    gamma1k = e1000/ener / volrat
    if debug:
        print(f'Energy scaling factors:\n\tgamma100 = {gamma100}' +
              f'\n\t gamma1000 = {gamma1k}')
        print('Velocity ratio factors (v_in/v_ext)**2:')
        print(f'\t1/100:  {(v_in/v100)**2}')
        print(f'\t1/1000: {(v_in/v1000)**2}')

    # Scale it up:
    n100 = n_in * gamma100 * (v_in/v100)**2
    n1000 = n_in * gamma1k * (v_in/v1000)**2

    return n100, n1000


def verify_gopal():
    '''
    Perform verification of Gopalswamy relations.
    '''

    print('Verifying B:')
    print(f'\tFor v=2000km/s, B={v_to_b(2000)} (expected: ~106nT)')

    print('Verifying V Weibull:')
    print('\tOccurrence rate for V=3800 = ' +
          f'1/{1/weibull(3800)} (1/100 expected)')
    print('\tOccurrence rate for V=4670 = ' +
          f'1/{1/weibull(4670)} (1/1000 expected)')

    print('Verifying INVERSE V Weibull:')
    print('\tVelocity of 1/100 storm = ' +
          f'{inv_weib(1/100)} (3800 expected)')
    print('\tVelocity of 1/1000 storm =  ' +
          f'{inv_weib(1/1000)} (4670 expected)')

    print('Verifying E Weibull:')
    print('\tOccurrence rate for E=4.4e+33 = ' +
          f'1/{1/weibull(4.4e+33, a=e_a, eta=e_eta, gamma=e_gam)} (1/100 expected)')
    print('\tOccurrence rate for E=9.8e+33 = ' +
          f'1/{1/weibull(9.8e+33, a=e_a, eta=e_eta, gamma=e_gam)} (1/1000 expected)')

    print('Verifying INVERSE E Weibull:')
    print('\tEnergy of 1/100 storm = ' +
          f'{inv_weib(1/100, a=e_a, eta=e_eta, gamma=e_gam)} (4.4e+33 expected)')
    print('\tEnergy of 1/1000 storm =  ' +
          f'{inv_weib(1/1000, a=e_a, eta=e_eta, gamma=e_gam)} (9.8e+33 expected)')


def gen_gopal_scalings(volrat=50):
    '''
    Using the assumptions in `summarize_extremes`,
    '''
    # Get values:
    b100, b1000 = v_to_b(v100), v_to_b(v1000)
    n100, n1000 = scale_dens(vmax_mean, nmax_mean, volrat=50)

    # Print'em out:
    print('1/100 scalings for MEAN:')
    print(f'V={.9*v100/vmax_mean}\tB={b100/bmax_mean}\tN={n100/nmax_mean}')
    print('1/100 scalings for MEDIAN:')
    print(f'V={.9*v100/vmax_medi}\tB={b100/bmax_medi}\tN={n100/nmax_medi}')
    print('1/1000 scalings for MEAN:')
    print(f'V={.9*v1000/vmax_mean}\tB={b1000/bmax_mean}\tN={n1000/nmax_mean}')
    print('1/1000 scalings for MEDIAN:')
    print(f'V={.9*v1000/vmax_medi}\tB={b1000/bmax_medi}\tN={n1000/nmax_medi}')


def summarize_extremes():
    '''
    For our 1/100 and 1/1000 event extremes, summarize the key
    peak values in the solar wind. Print assumptions to screen and create
    a markdown table of all values.
    '''

    # Get values:
    b100, b1000 = v_to_b(v100), v_to_b(v1000)
    n100, n1000 = scale_dens(vmax_mean, nmax_mean, volrat=50)

    # Print to screen.
    print('ASSUMPTIONS: ')
    print('\tVelocity slows by 10% from Corona to L1.')
    print('\tExtremes have volumes 50x larger than Katus vals.')
    print(f'|{"Freq (1/yr)":^13s}|{"Dist. Type":^13s}|{"$V$ ($km/s$)":^13s}' +
          f'|{"$E$ ($ergs$)":^13s}|{"90% $V$":^13s}|{"$B$ ($nT$)":^13s}' +
          f'|{"Dens ($ccm$)":^13s}|')
    print(f'|{13*"-"}|{13*"-"}|{13*"-"}|{13*"-"}|{13*"-"}|{13*"-"}|{13*"-"}|')

    # 1/100 year storm using Katus medians:
    print(f"|{'1/100':^13s}|{'Weibull':^13s}|{v100:^13.1f}|{e100:^13.3E}" +
          f"|{.9*v100:^13.1f}|{b100:^13.3f}|{n100:^13.3f}|")
    # 1/1000 year storm using Katus medians:
    print(f"|{'1/1000':^13s}|{'Weibull':^13s}|{v1000:^13.1f}|{e1000:^13.3E}" +
          f"|{.9*v1000:^13.1f}|{b1000:^13.3f}|{n1000:^13.3f}|")