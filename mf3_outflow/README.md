# MF3 Outflow Sensitivity Study

These input files are for running a sensitivity study on
"defacto"-type outflow (e.g., *Welling and Liemohn 2014*).
It uses the 3-fluid approach: $H^{+}_{sw}$, $H^{+}_{iono}$,
and $O^{+}_{iono}$. The inner boundary conditions and upstream
solar conditions are varied to investigate the sensitivity to
these factors of outflow fluence and magnetospheric composition.

There are 2 sets of input files in total:

- A basic single fluid run with BATS-R-US and the Ridley_serial ionosphere solver. Suffix of sf. 
- A multifluid simulation with BATS-R-US and Ridley designed for 3 fluid run. 

Each run comes in two stages: a steady state portion which starts the run with the specified initial conditions and the time-accurate portion, which is the main section of the run.

There is also a module file 'MultiIonoSWHO.f90' that needs to be implemented in the installation phase to run in a three-fluid configuration.

## Code Configuration

Installation:

```
./Config.pl -install= -compiler=[your compiler]
./Config.pl -o=GM:e=[MHD or MultiIonoSwHO]
```

## Default Simulation
Requires:
Solar wind input file with: bx, by, bz, ux, uy, uz, n, Rho (SW H+), HpRho (Iono H+), OpRho (Iono O+), t

Recommended Settings:
-#MULTIION
	- [Will add in recommended setting values here once run works]
-#COLLISION
	- [Will add in recommended setting values here once run works]



