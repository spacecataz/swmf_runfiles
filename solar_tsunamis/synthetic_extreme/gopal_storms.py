#!/usr/bin/env python3

'''
Create estimates for Gopalswamy storms
'''

import numpy as np

import matplotlib.pyplot as plt

plt.style.use('fivethirtyeight')

# Set some constants:
v_a, v_gam, v_eta = 3.5, 3.35379, 0.5  # Velocity coefficients
e_a, e_gam, e_eta = 3.1, 32.7, 1.9     # Energy coefficients

# Characteristics of Katus event:
vmax_mean = 639.39
vmax_medi = 612.6


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

    a2.loglog(e, weibull(e, a=e_a, eta=e_eta, gamma=e_gam))
    a2.set_xlabel('VEnergy ($erg$)')
    a2.set_ylabel('Occurrence ($\#/year$)')

    fig.tight_layout()


def v_plaw(years):
    '''
    Given an occurrence of 1/Y years, determine the approximate CME
    speed using the Gopalswamy powerlaw fitting.
    '''
    pass


def energy_to_dens(v_in):
    '''
    Given an extreme storm velocity, obtain the maximum density.
    '''

    # Energy/velocity for 1/100 and 1/1000 year storm:
    e100, e1000 = 4.4E33, 9.8E33
    v100, v1000 = 3800, 4670

    # Get the occurrence of storm, then obtain the energy in ergs.
    occ = weibull(v_in)
    ener = inv_weib(occ, a=e_a, eta=e_eta, gamma=e_gam)

    print(f'For a storm of velocity {v_in}, ' +
          f'occurrence is {occ:.1f} events/year and energy is {ener:.2E} ergs')

    # Get scaling factor:


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


def summarize_extremes():
    '''
    For our 1/100 and 1/1000 event extremes, summarize the key
    peak values in the solar wind.
    '''
    print(f'|{"Freq (1/yr)":13s}|{"Dist. Type":13s}|{"Max $V$":13s}' +
          f'|{"Total $E$":13s}|{"90% $V_max$":13s}|{"Max $B$":13s}' +
          f'|{"Dens":13s}')
    print(f'|{13*"-"}|{13*"-"}|{13*"-"}|{13*"-"}|{13*"-"}|{13*"-"}|{13*"-"}|')
