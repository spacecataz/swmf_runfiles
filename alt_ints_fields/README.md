# Alternative Intrinsic Fields

This subdirectory is for simulations with alternative intrinsic magnetic field configurations at Earth. Examples are weaker field strengths; tilted field configurations; and non-dipole configurations.

Runs currently in this directory:

## Weaker Field Configurations (WeakDip)
This run set experiments with weaker Earth intrinsic field strengths to test how the system responds to otherwise equivalent conditions. Relevant files have `weakdip` in the name.

Solar wind conditions are the idealized Katus et al. SEA medians for a CME with a sheath.

###  SWMF Configuration:
```
Config.pl -install=BATSRUS,RCM2,Ridley_serial
Config.pl -v=GM/BATSRUS,IE/Ridley_serial,IM/RCM2
make SWMF PIDL
```

Be sure to copy `magin_GEM.dat` into the run directory from the `common_files` directory.