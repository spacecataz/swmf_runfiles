# Idealized Substorm Simulations

These files are for producing idealized substorm simulations using the SWMF.

## Python Scripts
`create_imf.py` builds the IMF input files from scratch and plots Bz.
`msm.py` is a simple implementation of the Minimal Substorm Model.

## SWMF Configuration

Simple configuration with 2X IE resolution is recommended for these runs:
```
Config.pl -install= -compiler=gfortran
Config.pl -v=GM/BATSRUS,IE/Ridley_serial,IM/RCM2
Config.pl -o=IE:g=181,361
```

## PARAMs

The baseline param is based on the SWPC v2 runs with the following core changes:

- Ideal axes are used (no dipole tilt).
- No RB module.
- No CPCP-based inner boundary density variability.
- Higher density output for GM and IE.