This folder contains input files for running the SWMF with MAGNIT and electron pressure for the St. Patrick's Day storm of 2013.

Solar wind: taken from Wind (fewer data gaps than ACE) and ballistically propagated via `l1_propagate.py` in `SWMF_helpers`. For this event, conditions were elevated for a few days before the actual storm and the recovery was rather long as well, so the days before and after have been included in the file in case preconditioning ends up mattering.

To configure the SWMF for this run, run `make test_swpc_pe` in the SWMF directory. This is SWPC v2 res with a higher resolution ionosphere.
To configure manually:
`Config.pl -v=Empty,GM/BATSRUS,IE/Ridley_Serial,IM/RCM2
Config.pl -o=GM:e=MhdPe
Config.pl -o=IE:g=181,361`

IM params such as electron decay rate may need to be adjusted, as may the range of times simulated. 