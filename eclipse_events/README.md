# Eclipse Event Simulations

This folder is for simulations of events that occur during either partial or total eclipses.

## Dec. 4, 2021
This is an eclipse that occurred over the southern hemisphere across Antartica.
The goal of this simulation is to provide GM-IE-IM output for stand-alone GITM simulations. Focus is on 6-9UT.

Config and Install:
```
./Config.pl -install= -compiler=gfortran
./Config.pl -v=GM/BATSRUS,IE/Ridley_serial,IM/RCM2
./Config.pl -o=IE:g=181,361
make SWMF PIDL rundir
```

F10.7 values obtained from https://www.spaceweather.gc.ca/forecast-prevision/solar-solaire/solarflux/sx-5-flux-en.php?year=2021 ("adjusted" flux.)