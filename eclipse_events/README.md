# Eclipse Event Simulations

This folder is for simulations of events that occur during either partial or total eclipses.
Many of these runs require a new conductance model, "iModel 12", to be used.
This is simply a mode where the ionospheric conductance is simply read from
input files. To properly configure IE to use this new mode, the source files
in the `software` directory must be copied into the correct SWMF/IE directory
as shown below.

## Dec. 4, 2021
This is an eclipse that occurred over the southern hemisphere across Antartica.
The goal of this simulation is to provide GM-IE-IM output for stand-alone GITM simulations. Focus is on 6-9UT.

Update software to use iModel 12:
```
cp [path to repository]/swmf_runfiles/eclipse_events/*.f90 [path to SWMF directory]/IE/Ridley_serial/src/
```

Config and Install:
```
./Config.pl -install= -compiler=gfortran
./Config.pl -v=GM/BATSRUS,IE/Ridley_serial,IM/RCM2
./Config.pl -o=IE:g=181,361
make SWMF PIDL rundir
```

F10.7 values obtained from https://www.spaceweather.gc.ca/forecast-prevision/solar-solaire/solarflux/sx-5-flux-en.php?year=2021 ("adjusted" flux.)