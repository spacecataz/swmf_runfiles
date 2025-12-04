# Mesoscale CME Simulations

This folder contains inputs for investigating the impact of mesoscale
CME structures on the magnetosphere.

## Solar Wind Input Files
Solar wind input files are obtained via simulations of the SWMF-SH
component and driven by AWSOM-R. Virtual satellite extractions are used at
1$AU$ to be translated into SWMF Geospace inputs.

The included script, `sat_to_imf.py`, will convert SH output into GM input.

## Code Configuration
Configuration follows the standard SWPC-v2 setup without RBE. Other minor
changes are made for convenience (e.g., no timestep checking at the SWMF
level, no refreshing of the solar wind file).

Configuration follows the usual process:

```
./Config.pl -install=BATSRUS,RCM2,Ridley_serial
./Config.pl -v=GM/BATSRUS,IE/Ridley_serial,IM/RCM2
./Config.pl -o=IE:g=181,361
```
