# Fast Tail Flows

This folder contains inputs for performing very high resolution simulations
with the goal of producing localized fast flows in the tail.

## Code Config

Use the following commands to configure the SWMF for these simulations.
Note the resolution of IE, which yields 0.25$^{\circ}$ latitudinal grid
separation and 0.5$^{\circ}$ longitudinal grid.

```
git clone git@github.com:SWMFsoftware/SWMF.git

./Config.pl -install=BATSRUS,RCM2,Ridley_serial -compiler=[YOUR CHOICE]
./Config.pl -v=GM/BATSRUS,IE/Ridley_serial,IM/RCM2
./Config.pl -o=IE:g=361,721
```

## IMF input file information.

There are two IMF files. `imf_ideal.dat` is fully idealized inputs with a
simple southward turning. `imf_SH_mean_smoothed15.dat` is Katus SEA-based
inputs representing an idealized CME with a sheath.

## PARAM info
PARAM input files are based on the SWPC configuration but *much higher grid
resolution* in the global MHD portion.

Other small changes include the use of `#IDEALAXES` to remove dipole tilt and
deactivation of operational details (no re-read of IMF, etc.)

Version History
| # | Date | Updates |
|---|------|---------|
| 1 | Oct., 2024 | Initial successful PARAMs.
| 2 | Nov. 25, 2024 | Expanded high-res block; updated output to include raytracing |