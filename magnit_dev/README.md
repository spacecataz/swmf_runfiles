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