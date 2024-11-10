#!/usr/bin/env python3

'''
Create estimates for Gopalswamy storms
'''

import numpy as np

import matplotlib.pyplot as plt


# Set some constants:
a, gam, eta = 3.5, 3.35379, 0.5

def weibull(x, a=a, gamma=gam, eta=eta, m=1.0):
    '''
    For input `x`, return the corresponding `y` value using a Weibull
    distribution. Kwargs are Weibull parameters.
    '''

    X = np.log10(x)

    A1 = (gamma-X)/eta

    Y = a * (1-np.exp(-(A1)**m))

    return 10**Y


def inv_weib(y, a=a, gamma=gam, eta=eta, m=1.0):
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

    fig, (a1, a2) = plt.subplots(1, 2)

    a1.loglog(v, weibull(v))


def v_plaw(years):
    '''
    Given an occurrence of 1/Y years, determine the approximate CME
    speed using the Gopalswamy powerlaw fitting.
    '''
    pass


def v_weib(years):
    '''
    Given an occurrence of 1/Y years, determine the approximate CME
    speed using the Gopalswamy Weibull fitting.
    '''

    log_occur = 1


def energy_to_dens():
    '''
    Given an extreme storm
    '''