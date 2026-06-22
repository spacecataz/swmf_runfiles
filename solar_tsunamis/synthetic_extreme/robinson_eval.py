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
    avee = np.logspace(-1, 2, 1000, dtype=float)
    loc = (avee >= 0.4) & (avee <= 20)

    sigmap, sigmah = robinson(eflux, avee)
    ratio = sigmah / sigmap

    fig1 = plt.figure(figsize=(6, 8))
    gs = fig1.add_gridspec(4, 1, hspace=0)
    ax1 = fig1.add_subplot(gs[0, :])
    ax2 = fig1.add_subplot(gs[1:, :], sharex=ax1)

    ax1.loglog(avee, sigmap)
    ax2.loglog(avee, ratio)
    ax1.loglog(avee[loc], sigmap[loc], c='crimson', lw=2.)
    ax2.loglog(avee[loc], ratio[loc], c='crimson', lw=2.)
    ax1.set_xlim([0.1, 100])
    ax2.set_xlim([0.1, 100])
    ax1.set_ylim([.6, 10])
    ax2.set_ylim([0.01, 10])
    ax1.set_xticklabels('')
    ax1.set_ylabel(r'$\Sigma_P$ ($S$)')
    ax2.set_ylabel(r'$\Sigma_H/\Sigma_P$')
    ax2.set_xlabel(r'$\overline{E}$ ($keV$)')
    ax1.set_title('Robinson et al., 1987, Figure 1')
    fig1.tight_layout()


def illustrate_robinson():
    '''
    Show how the robinson formula saturates.
    '''

    # Average energy in keV
    avee = np.logspace(-1, 2, 1000, dtype=float)

    # Energy flux in ergs/cm3
    eflux = np.logspace(-1, 2, 1000, dtype=float)

    # Mesh it out.
    eflux, avee = np.meshgrid(eflux, avee)

    # Get conductance.
    sigmap, sigmah = robinson(eflux, avee)

    # Map it out!
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=[10, 6])
    fig.subplots_adjust(top=0.886, bottom=0.263, left=0.091,
                        right=0.964, hspace=0.2, wspace=0.281)
    cax = fig.add_axes([.25, .1, .5, .05])

    ckwargs = {'vmin': 0, 'vmax': 125}
    map1 = ax1.pcolormesh(eflux, avee, sigmap, **ckwargs)
    map2 = ax2.pcolormesh(eflux, avee, sigmah, **ckwargs)

    fig.colorbar(map1, cax, orientation='horizontal', label='$Siemens$')

    fig.suptitle('Robinson et al., 1987, illustrated')
    for ax, lab in zip([ax1, ax2], [r'$\Sigma_P$', r'$\Sigma_H$']):
        ax.set_title(lab)
        ax.set_xlabel('Energy Flux ($ergs/cm^3$)')
        ax.set_ylabel('Avg. Energy ($keV$)')