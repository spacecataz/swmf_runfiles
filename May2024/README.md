Solar wind propagation:

Wind HO level MFI and H1 level SWE data were downloaded from CDAWeb.
These two files were handed to `resample_sw.py` which removed bad
data, replaced them with NaNs, converted velocity from GSE to GSM
coordinates, calculated temperature from thermal velocity (W), and
saved the results in a CDF. That CDF was handed to `l1_propagate.py`
in `SWMF_helpers`, which propagated the results from L1 to the SWMF
inner boundary (no velocity smoothing was applied).

Included in this directory are the original Wind files from CDAWeb,
the merged CDF, the propagated file, a plot of the before and after
propagation, and the resampling script (requires pandas, scipy, and
spacepy). 