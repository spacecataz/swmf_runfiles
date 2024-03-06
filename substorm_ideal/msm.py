#!/usr/bin/env python3
'''
Freeman & Morley's Minimal Substorm Model.  Calculate the energy in the tail vs.
time using solar input from a SWMF-formatted ascii solar wind file.
See Freeman and Morley 2004, GRL.

Can be imported as a module or run as a stand-alone script that, upon reading
an SWMF-formatted IMF file, calculates substorm occurrence and system energy
state.

Requires Spacepy to read and hand IMF input.
'''

from argparse import ArgumentParser

import numpy as np
import matplotlib.pyplot as plt

from spacepy.pybats import ImfInput
from spacepy.plot import applySmartTimeTicks, style


def msm(imffile, D=2.69):
    '''
    Given an SWMF-formtted IMF file, run the minimal substorm model to
    predict substorm occurrence. The results are saved as the time-varying
    energy within the system and a list of epochs of substorm expansions.
    The values are saved within the input ImfInput object as
    `ImfFile['energy']` and `ImfFile.attrs['msm_epochs']`.

    Parameters
    ----------
    imffile : string or spacepy.pybats.ImfInput object
        The IMF conditions used to drive the model.
    D : Float, defaults to 2.69
        Substorm time constant, in hours.

    Returns
    -------
    imf : spacepy.pybats.ImfInput object
        The IMF conditions used, including the energy and epoch list as
        described above.
    '''

    # Convert time constant from hours to seconds:
    D *= 3600.

    # Open file (or rename if already opened.)
    if type(imffile) is str:
        imf = ImfInput(imffile)
    elif type(imffile) is ImfInput:
        imf = imffile
    else:
        raise TypeError(f'Unrecognized file type: {type(imffile)}')
    imf.calc_epsilon()

    # Create results containers:
    n_pts = imf['time'].size
    energy = np.zeros(n_pts)
    epochs = []

    ener_last = D*imf['epsilon'].mean()
    energy[0] -= ener_last

    # Integrate:
    for i in range(1, n_pts):
        dt = (imf['time'][i]-imf['time'][i-1]).total_seconds()
        energy[i] = energy[i-1]+imf['epsilon'][i]*dt

        if energy[i] >= 0:
            ener_last = D*imf['epsilon'][i]
            energy[i] = - ener_last
            epochs.append(imf['time'][i])

    # The results are stored within the IMF object itself:
    imf['energy'] = energy
    imf.attrs['msm_epochs'] = epochs

    # Return IMF.
    return imf


def plot_msm(imf, title='Minimal Substorm Model'):
    '''
    Create a plot showing the MSM results for the given ImfInput object that
    has already been processed by the `msm` function.

    Parameters
    ----------
    imf : spacepy.pybats.ImfInput object
        The IMF conditions, including MSM results, to plot.
    title : str, default='Minimal Substorm Model'
        Set the plot title.

    Returns
    -------
    fig : Matplotlib Figure object
        The figure containing the generated plots.
    '''

    style()

    # Grab epochs for convenience:
    epochs = imf.attrs['msm_epochs']

    # Create figure object and axes objects.
    fig, (a1, a2) = plt.subplots(2, 1, figsize=[8, 6])

    # Create line plots:
    a1.plot(imf['time'], imf['epsilon'], 'r-', lw=2)
    a2.plot(imf['time'], imf['energy'], '-', lw=2)

    # Create and label horizontal threshold line:
    a2.text(imf['time'][0], 0.05, '  Substorm Energy Threshold')
    a2.hlines(0.0, imf['time'][0], imf['time'][-1],
              linestyles='dashed', lw=2.0, colors='k')

    # Place epochs onto plot, preserving y-limits.
    ymin, ymax = a2.get_ylim()        # get current axis limits.
    ymax = .2                         # add some space above zero.
    a2.vlines(epochs, ymin, ymax, colors='maroon', linestyles='dashed')
    a2.set_ylim([ymin, ymax])         # restore ylimits to good values.

    # Y-axes labels:
    a1.set_ylabel('Solar Wind Power', size=14)
    a2.set_ylabel('Tail Energy State', size=14)

    # Y-axis ticks:
    a1.set_yticklabels('')
    a2.set_yticklabels('')

    # Plot title:
    a1.set_title(title)

    # Set time ticks:
    applySmartTimeTicks(a1, imf['time'])
    applySmartTimeTicks(a2, imf['time'], True)

    fig.tight_layout()


# ##### BEGIN MAIN PROGRAM:
if __name__ == '__main__':
    # Build and populate argparser:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('imffile', type=str,
                        help='The name of the IMF input file to read.')
    parser.add_argument('-D', '--D', type=float, default=2.69,
                        help='Value of the substorm time constant. ' +
                        'Defaults to 2.69 hours.')
    parser.add_argument('-t', '--title', type=str, help='Set figure title.',
                        default='Minimal Substorm Model')

    # Get args from caller, collect arguments into a convenient object:
    args = parser.parse_args()

    # Run the MSM:
    imf = msm(args.imffile, D=args.D)

    # Create plot:
    fig = plot_msm(imf, title=args.title)

    # Show figure:
    plt.show()
