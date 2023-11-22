#!/usr/bin/env python3

'''
A set of helper functions for handling the SEA upstream driver files:

- *smooth_imf* will use a median filter to remove excess noise.
- *intensify_storm* can be used to change the magnitude of the IMF drivers.

'''

from copy import copy

import numpy as np

from spacepy.datamodel import dmarray
from spacepy.pybats import ImfInput


def smooth_imf(imffile, varlist=['ux'], do_write=False, window=31):
    '''
    Given a path to an IMF input file or an IMF object, *imffile*,
    smooth all variables listed under *varlist* using Scipy's median filter
    function with a 31 minute window (can be changed using kwarg *window*).

    The resulting data will be saved to a new file with `smooth{window}`
    appended to file name if the kwarg *do_write* is set to `True`.

    The default action is to only smooth radial velocity.
    '''

    from scipy.signal import medfilt

    # If ImfInput is an existing object, just use it.  Else, open the data.
    imf = copy(imffile) if type(imffile) is ImfInput else ImfInput(imffile)

    for v in varlist:
        imf[v] = medfilt(imf[v], window)

    # Overwrite imf['v']:
    if 'v' in imf:
        imf['v'] = dmarray(np.abs(imf['ux']),
                           {'units': 'km/s', 'label': '$km/s$'})

    imf.attrs['file'] = imf.attrs['file'][:-4] + f'_smoothed{window}' \
        + imf.attrs['file'][-4:]
    if do_write:
        imf.write()

    return imf


def generate_scaling(x, amp, x_rise, x_fall, lamb_rise, lamb_fall):
    '''
    Create a hyberbolic tangent function to scale a storm with a stronger
    onset that decays away to background values again after a set amount of
    time.

    Parameters
    ----------
    x : :class:`np.ndarray`
       A 1-dimensional array representing the independent variable against
       which the scaling function will be applied.
    amp : :class:`float`
       The normalized amplitude for the peak.
    x_rise : :class:`float`
       The point in *x* at which scaling increases from 1 towards the peak.
    x_fall : :class:`float`
       The point in *x* at which scaling decreases back towards 1.
    lamb_rise : :class:`float`
       The period of the rise in the scaling function towards *amplitude*.
    lamb_fall : :class:`float`
       The period of the fall in the scaling function as it returns to 1.
    '''

    # Alter amplitude to account for the fact that we're adding together
    # two hyp. tangents, both with minima of 1.
    amp = amp/2-.5

    # Sum the two hyperbolic tangents:
    y = amp*np.tanh(2*np.pi/lamb_rise*(x-(x_rise+lamb_rise/2))) - \
        amp*np.tanh(2*np.pi/lamb_fall*(x-(x_fall+lamb_fall/2))) + 1

    return y


def scale_imf(imffile, epoch_rise, epoch_fall, lamb_rise, lamb_fall,
              amp=5, outfile=None, ufactor=5):
    '''
    Given a path to an IMF input file, *imffile*, scale the solar drivers to
    amplify the storm by a factor of *amp* for a period between *epoch_rise*
    and *epoch_fall*.

    Parameters
    ----------
    imffile : :class:`str` or :class:`~spacepy.pybats.ImfInput`
       The IMF data or name of the IMF file to alter.
    epoch_rise : :class:`datetime.datetime`
       The time at which scaling increases from 1 towards the peak.
    epoch_fall : :class:`datetime.datetime`
       The time at which scaling decreases back towards 1.
    lamb_rise : :class:`float`
       The period of the rise in scaling towards *amp* (in minutes).
    lamb_fall : :class:`float`
       The period of the fall in scaling as it returns to 1 (in minutes).
    amp : :class:`float` or :class:`dict`, default 5
       The normalized amplitude for the peak.
       If a float is given, the same scaling is applied to all variables.
       If a dictionary is given, it should contain variable name-amplitude
       pairs. Only values within the `amp` dictionary will have scaling
       applied.
    outfile : :class:`str`, default None
       If provided, the path/name to save the altered IMF data.
    ufactor : :class:`int`, default 5
       Velocity (ux, etc.) falls off more slowly than other values.
       *lamb_fall* is multiplied by *ufactor* when the scaling is applied
       to velocity components.

    Returns
    -------
    :class:`~spacepy.pybats.ImfInput`
       The IMF file object scaled.
    :class:`~numpy.array`
       The scaling function applied to the data.

    '''

    from matplotlib.dates import date2num

    # If ImfInput is an existing object, just use it.  Else, open the data.
    imf = copy(imffile) if type(imffile) is ImfInput else ImfInput(imffile)

    # Convert the datetimes to floating points:
    epoch_rise = date2num(epoch_rise)
    epoch_fall = date2num(epoch_fall)
    time = date2num(imf['time'])

    # Convert lambdas from minutes to days:
    lamb_rise /= 1440.
    lamb_fall /= 1440.

    # Handle amplitudes. If just a single floating point value,
    # convert into dictionary with amplitude applied to all values.
    if type(amp) is float or int:
        amp = dict([[v, amp] for v in imf.attrs['var']])

    # Generate scaling functions:
    scales = {}
    for v in amp:
        isU = v[0] == 'u'  # Separate time scalings for velocities.
        scales[v] = generate_scaling(time, amp[v], epoch_rise, epoch_fall,
                                     lamb_rise, lamb_fall*(1+ufactor*isU))

    # Scale velocity separately- it decays much slower.
    # scale_u = generate_scaling(time, amp, epoch_rise, epoch_fall,
    #                           lamb_rise, lamb_fall*ufactor)

    # Apply to all variables:
    for v in scales.keys():  # imf.attrs['var']:
        imf[v] *= scales[v]

      #  if v[0] == 'u':
      #      imf[v] *= scale_u
      #  else:
      #      imf[v] *= scale

    # Overwrite imf['v']:
    if 'v' in imf:
        imf['v'] = dmarray(np.abs(imf['ux']),
                           {'units': 'km/s', 'label': '$km/s$'})

    # Save file if requested:
    if outfile:
        imf.attrs['file'] = outfile
        imf.write()

    return imf, scales
