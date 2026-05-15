# Real Time Runs

This folder contains PARAMs and inputs for running the SWMF in real time
on NASA HPE machines.

Supporting scripts can be found in the
[SWMF Helpers repository](https://github.com/spacecataz/SWMF_helpers),
including [`gen_ace_realtime.py`](https://github.com/spacecataz/SWMF_helpers/blob/master/gen_ace_realtime.py)

Note that IMF input files are provided for "post-event" analysis - runs
performed after the fact, but still in a "real time manner". These files are
built using SWPC archived ACE and DSCOVR real-time data stream values
(as opposed to cleaned, science-quality data found on CDAweb).

## Notes on creating solar wind drivers post-event
Archived

Solar wind and IMF values for post-event runs are obtained and processed
as follows:

 - DSCOVR NetCDF files are obtained from [NGDC's data portal](https://www.ngdc.noaa.gov/dscovr/portal/index.html).
 - ACE ASCII files are obtained from the [ACE FTP Server](ftp://ftp.swpc.noaa.gov/pub/lists/ace/).

Use the included script `convert_rtace.py` to convert a set of ACE ASCII files
into an IMF input file (propagation options set in arguments). The default
behavior is to use ballistic propagation and an 11-minute smoothing window on
velocity.
