The two PARAMs in this file should work for electron pressure MAGNIT runs.

This folder has been updated to just contain the current verified standard configuration run with an inner boundary of 2.0.
This is the PARAM.in.init_MAGNIT_Pe file. In addition, the provided IMF file is set up to work well with MAGNIT Pe.
It contains propagated data from ACE for the Galaxy event, along with combined electron temperature information from WIND.

To change your SWMF configuration to the configuration MAGNIT has been tested with, there are two options:
- "make test_swpc_pe" will automatically change all parts of the configuration to be correct.
- To make the same changes manually, run:
```
Config.pl -v=Empty,GM/BATSRUS,IE/Ridley_Serial,IM/RCM2
Config.pl -o=GM:e=MhdPe
Config.pl -o=IE:g=181,361
```

If you have any questions/trouble, feel free to reach out to me at arigott@umich.edu

## Available PARAMs
The following PARAMs simulate the April 2010 "Galaxy 15" super substorm event:
- `PARAM.in.init_MAGNIT_pe` uses MAGNIT with electron pressure.
- `PARAM.in.init_RLM` uses the Ridley Legacy conductance model.

## Notes on PARAM.in Development
Outside of basic changes to output types/frequencies, the following changes
have been made compared to the defacto standard SWPC PARAM input file:

- Operational options are deactivated (e.g., `#CHECKTIMESTEP`, `#REFRESHSOLARWINDFILE`, etc.)
- All RB-related commands are removed.
- No `#STRICT`.
- The MHD inner boundary has been reduced to 2.0 RE; $R_{currents}$ to 2.5. The 1/8 $R_E$ grid resolution region extends to 2.0 $R_E$.
- The MHD IB density is increased to 40 $AMU/cm^3$.
- `#CPCPBOUNDARY` has been removed.
- Ridley_serial is configured to use MAGNIT, including changes to solver parameters.
- RCM is configured to use a 90/10 H+/O+ ratio, max outer boundary location, and updated precipitation loss values.



