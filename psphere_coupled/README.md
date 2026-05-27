# Contents
This folder contains modified files for several SWMF compatable models and PARAM files for running simulations within the SWMF. The purpose of these files is to study plasmasphere recirculation, espcially with a two-way coupled plasmasphere. 

The readme is broken down into three sections: Instructions for installing the SWMF modified in the appropiate manner to run some of the simulations with provided PARAM files, a notes section detailing the current state of the reaserch, and a record of the contents of the psphere_coupled folder, namely the contents of the Modified SWMF files and the purpose of the various files containing the PARAM files. 


# GM-PS-IE Simulations

These runs are for exploring coupling between the plasmasphere physics
module (currently occupied by DGCPM) with the GM module (multifluid
BATS-R-US.)

# GM-IM-IE/CIMI Simulations

These runs are to test the evolution of the inner-magnetosphere in the presence of a two-way coupled plasmasphere (See Bagby-Wright et al. 2023). 

Use the MHD equation file: `ModEquationRecircPe.f90` found in the 'ModifiedSWMFFiles/GM/' folder and place this file into `SWMF/GM/BATSRUS/srcEquation`.
This will configure BATS-R-US to use two fluids: Hp and HpPs.
The first fluid is a combined solar/polar ion outflow fluid representing
a "typical" MHD simulation.  The second fluid is for the recirculating
plasmasphere material.

Use the CIMI equation file: `ModEquationReHpsH.f90` found in 'ModifiedSWMFFiles/IM/src/' and place this file into the 'IM/CIMI/src' directory. 

If from a fresh install of SWMF and not cloned from mudtop's (on github) fork of the normal SWMFsoftware version of the SWMF and component models, some changes to Config files will need to be made for BATS, and CIMI as well as share/Library/src/ModProcessVarName.f90. 

The changes are those needed so that each model can see the new equation files, as well as the shared library having the variables associated with the recirculating plasmasphere defined. 
(seriously though just clone mudtop's). 

## SWMF Configuration for GMIMIE:
```
Config.pl -install
Config.pl -v=GM/BATSRUS,IE/Ridley_serial,IM/CIMI
cp [Path to this repository]/swmf_runfiles/psphere_coupled/ModEquationRecircPe.f90 [Path to SWMF install directory]/GM/BATSRUS/srcEquation/
Config.pl -o=GM:e=RecircPe,IM:EarthReHpsH,GridExpanded
make SWMF PIDL
```
### Remake SWMF Macro
```
./Config.pl -uninstall
./Config.pl -install
./Config.pl -v=GM/BATSRUS,IE/Ridley_serial,IM/CIMI
./Config.pl -o=GM:e=RecircPe,IM:EarthReHpsH,GridExpanded
make SWMF PIDL
```
### Remake SWMF Macro - Full
```
make clean
./Config.pl -uninstall
./Config.pl -install=BATSRUS,CIMI,Ridley_serial
./Config.pl -v=GM/BATSRUS,IE/Ridley_serial,IM/CIMI
./Config.pl -o=GM:e=RecircPe,IM:EarthReHpsH,GridExpanded
make SWMF PIDL
```

### SWMF Configuration for GMPSIE:
```
Config.pl -install=BATSRUS,DGCPM,Ridley_serial
Config.pl -v=GM/BATSRUS,IE/Ridley_serial,PS/DGCPM
Config.pl -o=GM:e=MultiSwIono
make SWMF PIDL
```
## Simulations

### PLASCIRC_POC
This is the proof-of-concept run to test if we can create psuedo-plumes
in multifluid BATS.  It uses #MAGNETOSPHERE and #POLARBOUNDARY to restrict
IB densities about the equator.  This grows into a plasmasphere that forms
a plume under southward IMF conditions.

### PSGMIE_SIMPLE1WAY
This run is nearly the same as the PlasCirc_PoC runs in entryMF, but
GM is only single fluid and the IE potential is used to drive DGCPM.
Don't forget your test satellites!

### PSGMIE_POC
This is the proof-of-concept simulation for PS->GM coupling.  It is the same
as PlasCirc_PoC except that PS is turned on and is coupling into one of
the GM fluids.

## Notes

### General Notes about common Problems

### 5/27/2026

Updating SWMF to latest version on all platforms and ensuring that BATS-CIMI two-way coupling is still functional. 