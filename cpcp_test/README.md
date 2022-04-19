# CPCP Tests

This directory contains a set of run files to reproduce the simulations from
Welling & Zaharia, GRL, 2012. The goal is to examine the hypothesis that the
cross polar cap potential reductions associated with polar wind outflows
(i.e., lower CPCP than simulations without such outflows) arise from the same
mechanism that drives CPCP reductions when a ring current module is included.
The mechanism in question is a change in the shape of the magnetosphere to be
a more blunt obstacle to the solar wind flow, changing the force-balance in
the sheath and reducing the geoeffective length in the upstream solar wind.

There are four sets of input files in total:

- A basic run with only BATS-R-US and the Ridley_serial ionosphere solver (files wihtout an extra suffix)
- A simulation with BATS, Ridley, and the Rice Convection Model (RCM). Related files have the extra suffix `.rcm`.
- A simulation with BATS, Ridley, and the Polar Wind Outflow Model (PWOM). Related files have the extra suffix `.pw`.
- A simulation with BATS, Ridley, RCM, and PWOM. Related files have the extra suffix `.all`.

Each run comes in two stages- the steady state portion which creates an initial
condition for the remainder of the run (`PARAM.in.ss*`) and the time-accurate
portion, which is the main section of the run (`PARAM.in.ta*`).

## Configuration and Compilation

To run any of the simulations, install and configure with all the required
modules/codes, even if you are only using a subset. Compile and create a
run directory.

```
./Config.pl -install=<codes if not cloned> -compiler=<compiler>
./Config.pl -v=GM/BATSRUS,IE/Ridley_serial,IM/RCM2,PW/PWOM
make SWMF PIDL
make rundir
```

Enter the run directory and copy over all run files.

## Create PWOM Initial Conditions

If you are using PWOM, it will be necessary to create a steady-state restart
file set using `PARAM.pw.ss`, then move those files into PWOM's restart dir.
This requires a few steps: creating the initial field line objects, running
PWOM in steady state mode, saving the restart lines for later use, and
copying them to the appropriate place before running PWOM in time-accurate
mode.

From within the run directory:

```
cp ../PW/PWOM/Scripts/CreateRestart.pl PW/restartIN/
cd PW/restartIN
./CreateRestart.pl
```

Then, return to the run directory and execute the steady-state PW run:

```
rm -f PARAM.in LAYOUT.in
ln -s PARAM.pw.ss PARAM.in
ln -s LAYOUT.in.pwss LAYOUT.in
```

...execute using mpirun, jobscripts, etc.

Once this portion has finished, stash the files and copy to PWOM's restartIN
directory:

'''
cp -r PW/restartOUT ./PW_initfiles
cp PW_initfiles/* PW/restartIN/
'''

## Running Simulations

Replace the default PARAM and LAYOUT files with relevant set:

```
rm -f PARAM.in LAYOUT.in
ln -s PARAM.in.ss.all PARAM.in
ln -s LAYOUT.in.all LAYOUT.in
```

Once the steady state is finished, use Restart.pl and perform the time-accurate
portion:

```
./Restart.pl
rm -f PARAM.in
ln -s PARAM.in.ta.all PARAM.in
```

Note that `LAYOUT.in.all` should always be used.

Then, just execute the SWMF via MPI or requisite jobscript.