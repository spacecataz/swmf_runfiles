# GM-PS-IE Simulations

These runs are for exploring coupling between the plasmasphere physics
module (currently occupied by DGCPM) with the GM module (multifluid
BATS-R-US.)

##PLASCIRC_POC
This is the proof-of-concept run to test if we can create psuedo-plumes
in multifluid BATS.  It uses #MAGNETOSPHERE and #POLARBOUNDARY to restrict
IB densities about the equator.  This grows into a plasmasphere that forms
a plume under southward IMF conditions.

##PSGMIE_SIMPLE1WAY
This run is nearly the same as the PlasCirc_PoC runs in entryMF, but
GM is only single fluid and the IE potential is used to drive DGCPM.
Don't forget your test satellites!

##PSGMIE_POC
This is the proof-of-concept simulation for PS->GM coupling.  It is the same
as PlasCirc_PoC except that PS is turned on and is coupling into one of
the GM fluids.

##SWMF Configuration:
```
Config.pl -install=BATSRUS,DGCPM,Ridley_serial
Config.pl -v=GM/BATSRUS,IE/Ridley_serial,PS/DGCPM
Config.pl -o=GM:e=MultiSwIono
make SWMF PIDL
```

#GM-IM/CIMI Simulations

Use the MHD equation file: `ModEquationRecircPe.f90`

Place this file into `GM/BATSRUS/srcEquation`
