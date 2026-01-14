PARAMs:

There are PARAM files for three configurations in this directory.

`PARAM.in_init_rlm_medres` is for a run with the standard SWPC v2
configuration (run `make test_swpc` to configure the SWMF).

`PARAM.in_init_rlm_1.75_medres` is for a run with mostly standard
SWPC v2 configuration (again, `make test_swpc`), but with the inner
MHD boundary lowered from the standard 2.5 RE to 1.75 RE. Because
of the lowered inner boundary, `Rho0Cpcp` has also been increased
to 50.

`PARAM.in_init_rlm_ua_medres` is for a run with the standard SWPC v2
configuration, but with the addition of GITM two-way coupled. Be
sure to run (note that this might change since the GITM coupling is
being actively worked on)
```
./Config.pl -install=BATSRUS,RCM2,Ridley_serial,GITM -compiler=[YOUR CHOICE]
./Config.pl -v=GM/BATSRUS,IE/Ridley_serial,IM/RCM2,UA/GITM
```

Solar wind propagation:

Wind H0 level MFI and H1 level SWE data were downloaded from CDAWeb.
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

MMS data: these data are not propagated; rather, they have simply
been downsampled from the FGM and HPCA survey-level data to 1 min.
Data points when MMS reentered the magnetosheath have been dropped
and linearly interpolated over.
