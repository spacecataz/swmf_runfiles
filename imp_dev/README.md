# SWMF Inner magnetosphere precipitation 
These files are the currently used PARAMs for running the SWMF
with the IMP precipitation/conductance model.

To set up the SWMF configuration, install as follows:
```
git clone git@github.com:SWMFsoftware/SWMF.git


./Config.pl -install=BATSRUS,CIMI,Ridley_serial -compiler=[YOUR CHOICE]
./Config.pl -v=GM/BATSRUS,IE/Ridley_serial,IM/CIMI
./Config.pl -o=IE:g=181,361
./Config.pl -o=IM:gridexpanded,earthho
./Config.pl -o=GM:e=MhdAnisoP
```

or let the SWMF set the configuration by running

```
git clone git@github.com:SWMFsoftware/SWMF.git

make test_swpc_cimi_compile -j
```

PARAM.in_imp is the standard param configuration for running IMP without
GITM.

# GITM Coupling
GITM coupling currently only works with the couple2swmf branch of GITM.

IMP can be coupled with GITM 1 or 2 ways. When coupled,
each precipitation type can individually be selected for use by
changing the #AURORATYPES command in the GITM section of the PARAM.

In order to reduce issues when starting simulations, GITM's conductance
is set up to not be used for the first 5 minutes of the time accurate
solution. This allows for gitm to reach a more stable solution before
the conductance is used in the IE solver.

To add in GITM, run

```
./Config.pl -v=UA/GITM
```

PARAM.in_gitm is the standard param configuration for running IMP with
GITM.