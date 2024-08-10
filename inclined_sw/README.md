# Inclined Solar Wind Simulations

This directory is for simulations with inclined solar wind shock fronts.

## Ideal Inclined Runs
The `ideal_incl` directory contains files for running simple scenarios where simple solar wind transients (sudden impulses, southward turnings) occur at different inclinations. High resolution output is used to characterize the response.

## Code Configuration
```
./Config.pl -install=BATSRUS,Ridley_serial # Optional:RBE, RCM2
./Config.pl -v=GM/BATSRUS,IE/Ridley_serial
./Config.pl -o=IE:g=181,361
```