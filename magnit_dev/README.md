The two PARAMs in this file should work for electron pressure MAGNIT runs.

"init_MAGNIT_SWPC" uses the default configuration of resolutions, while "init_MAGNIT_storm" pushes the inner boundary to 1.5 Re.
As a result, the former runs at around 3x real time on 500 CPUs, while the latter runs at around 1.5x real time, as other corrections have to be made to prevent crashes near the inner boundary.

To change your SWMF configuration to the configuration MAGNIT has been tested with, there are two options:
- "make test_swpc_pe" will automatically change all parts of the configuration to be correct.
- To make the same changes manually, run:
```
Config.pl -v=Empty,GM/BATSRUS,IE/Ridley_Serial,IM/RCM2
Config.pl -o=GM:e=MhdPe
Config.pl -o=IE:g=181,361
```

If you have any questions/trouble, feel free to reach out to me at arigott@umich.edu