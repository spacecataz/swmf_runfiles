# Superposed Epoch Analysis-based Storm Drivers

**THE DATA PROVIDED HERE IS CURTOUSEY OF DR. ROXANNE KATUS.**
**BEFORE USING THESE FILES, SEEK PERMISSION/COUNSEL FROM DR. KATUS**

These solar wind input files have been obtained via a normalized timeline superposed epoch analysis (SEA) performed by *Katus et al.,*, 2016.
Three types of nominal events are included: an ideal corotating interaction region (CIR), an ideal magnetic cloud CME (MC), and an idea sheath-driven CME (SH).
Files for both the SEA mean and median are included.

It should be noted that the results produced by this module are not yet physically consistent across 
each variable. Further work is in progress to alleviate this shortcoming.

# Recommended Settings & Considerations

## F10.7 Flux
| Storm Type  | F10.7 (sfu) |
| ----------- | ----------- |
| MC-CME      | 200.0       |
| SH-CME      | 200.0       |
| CIR	      | 125.0	    |

## Smoothing Values
The mean and median values can be excessively noisy, especially for velocity.
Users may consider filtering the data.  In Python:

```
from scipy.signal import medfilt
from spacepy.pybats import ImfInput

imf = ImfInput('./imf_SH_mean.dat')
imf['ux'] = medfilt(imf['ux'], 31)

imf.attrs['file'] = 'imf_SHmean_smoothed.dat'
imf.write()
```

Users may also consider smoothing IMF Bx, as it does not converge with the
SEA analysis as well as other components.

## Storm Epochs/Timing
All files start arbitrarily on 2000-01-01T00:00:00UT.
This date/time is selected for convenience only.
Based on this start time, approximate storm onsets are given in the table below.

## Amplitude Scaling
It is possible to scale the events to achieve stronger or weaker storms.
For details, see the `scale_imf` function within the process_drivers.py file.
Suggested parameters are given below; users are encouraged to experiment.

| Storm Type | Onset Epoch         | Rise Time | Decay Epoch         | Fall Time |
| ---------- | ------------------- | --------- | ------------------- | ----------|
| MC-CME     | | | | |
| SH-CME     | 2000-01-01T08:15:00 | 2 hours   | 2000-01-01T21:00:00 | 12 hours |
| CIR	     | | | | |

An example usage is given below:

```
import datetime as dt
from process_drivers import scale_imf

start = dt.datetime(2000,1,1,8,15,0)
stop = dt.datetime(2000,1,1,21,0,0)

imf, scale = scale_imf('./imf_SH_mean.dat', start, stop, 120, 720)
```

# Python Code
Several scripts are provided to help handle these files:

- *create_drivers.py* will convert the source Matlab files into SWMF input files.
- *plot_drivers.py* will create a set of quick-look plots.
- *process_drivers.py* contains a set of functions for handling and editing the files.

Note that [Spacepy](https://spacepy.github.io/) is required.

# Acknowledgements & Further Reading
The data for these input files have kindly been provided by Dr. Roxanne Katus, Eastern Michigan University.

Details on the included data and processing can be found in the following paper:

Katus, R. M. R. M., Liemohn, M. W. M. W., Ionides, E. L. L., Ilie, R., Welling, D. T., & Sarno-Smith, L. K. K. (2015). Statistical analysis of the geomagnetic response to different solar wind drivers and the dependence on storm intensity. Journal of Geophysical Research: Space Physics, 120(1), 310–327. [https://doi.org/10.1002/2014JA020712](https://doi.org/10.1002/2014JA020712)
