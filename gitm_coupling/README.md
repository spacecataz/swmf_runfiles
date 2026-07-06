# GITM-SWMF Coupling
These files are for developing and testing updated GITM-SWMF coupling,
including one-way SWMF->GITM coupling.

## Code Installation and Setup

Obtain models from respective repositories. Switch to the SWMF coupling branch on GITM:

```
git clone --depth 1 git@github.com:SWMFsoftware/SWMF.git

cd SWMF/UA
git clone git@github.com:GITMCode/GITM.git

cd GITM
git switch couple2swmf
```

Back at the top-level SWMF directory, install via the usual approach:

```
./Config.pl -install=BATSRUS,RCM2,Ridley_serial -compiler=[YOUR CHOICE]
./Config.pl -v=GM/BATSRUS,IE/Ridley_serial,IM/RCM2,UA/GITM
./Config.pl -o=IE:g=181,361

make SWMF PIDL
```

## Files for Steady State Creation
GITM requires a good steady state solution once we transition to a storm event.
The folder "createSS" create a very simple steady state/quiet time solution
that can be used for other events.

These files are for GITM-standalone; the resulting restart can be used in
other simulations.

## Idealized Simulation Files
A super simple idealized simulation is provided to test coupling, including
the impact of the neutral wind dynamo on FACs.

## LWS Coupling
These are files for the LWS-GIC project where we evaluate the role of the
thermosphere in the development of ground magnetic disturbances.