#!/usr/bin/env python

'''
Evaluate the Robinson formula across a range of values.
Push past the 40keV limit and test possible fixes.
'''

import numpy as np
import matplotlib.pyplot as plt


def robinson(eflux, avee, limit=True):
    '''
    Perform the robinson conductance calculation.

    Parameters
    ----------
    eflux, avee : floats or arrays of floats.
        The precipitating average energy and energy flux.
        Energy flux should be in units of ergs/cm2.
        Average energy should be in units of keV.

    Returns
    -------
    sigmap, sigmah : same dtype as inputs
        The resulting Pedersen and Hall conductances, in Siemens.
    '''

    sigmap = np.sqrt(eflux) * (40. * avee) / (16. + avee**2)
    sigmah = 0.45 * sigmap * avee**0.85

    # SigmaPOut_II = sqrt(cond_Eflux_II) * (40. * cond_AvgE_II) / (16. + cond_AvgE_II**2)
    # SigmaHOut_II = 0.45 * SigmaPOut_II * cond_AvgE_II**0.85

    return sigmap, sigmah


def test_robinson():
    '''
    Reproduce plots from the Robinson paper to verify we got it right.
    '''

    # Figure 1:
    eflux = 1
    avee = np.logspace(-1, 2, 50, dtype=float)
    sigmap, sigmah = robinson(eflux, avee)

    fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(6, 8))

    ax1.loglog(avee, sigmap)
    ax2.loglog(avee, sigmah / sigmap)


def illustrate_robinson():
    avee = np.logspace(-1, 2, 50, dtype=float)