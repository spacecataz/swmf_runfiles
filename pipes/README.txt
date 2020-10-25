This is the updated "in the pipes" run input set.  The goal is to test
the hypothesis that outflow can build up in the lobes pre-storm to change
the strength of storm onset in terms of ring current build up, etc.

The storm is completely idealized and starts at 12UT with a sudden
commencement and a southward turning of the IMF.  Pre-storm, there is a
weakly southward IMF configuration to get things worked up a bit.

Two runs are utilized here:

TIME:  00UT-------------10----12----------------00UT
Run A: |---PWOM 1-way---|-------PWOM 2way-------|  # no preconditioning?
Run B: |---PWOM 2-way---------------------------|  # preconditioning?

Status of Runs:
===============
These runs are non-trivial!  The current status is to,
--Use RCM as RAM-SCB does not compile with SWMF in a trival manner.
--Use single fluid MHD as the RCM-MHD species coupling is poorly implemented.

PARAM Layout:
============
Both: Use PARAM.in.ss to set up steady state.
Run A: Use PARAM.in.1way until completion; then restart with PARAM.in.2way
Run B: Use PARAM.in.2way until completion.

Run Configuration:
==================
These runs require either RCM or RAM-SCB.
Obtain the RAM-SCB source and drop it into the IM folder, or just use RCM.

Set up the code as follows (RCM)
```
./Config.pl -v=Empty,GM/BATSRUS,IE/Ridley_serial,IM/RCM2,PW/PWOM
./Config.pl -o=GM:u=Default,e=Mhd
```

Here is the incomplete and untested version that would use RAM-SCB:
```
./Config.pl -install=BATSRUS,PWOM,Ridley_serial -compiler=<choice> -openmp
./Config.pl -v=GM/BATSRUS,IE/Ridley_serial,PW/PWOM,IM/RAM_SCB
./Config.pl -
```

Test satellites (stationary sats for probing) must be copied to rundir.

PWOM outflow lines must be created on initial restart.  Use the CreateRestart.pl
script with nCirc=8 (yields 216 lines).  For this run, the northern
hemisphere is reflected to the south.


Library Locations
=================
Here are some tips on setting library locations for RAM:
OSX:
-gsl=/opt/local/lib/
-netcdf=/opt/local/lib/
