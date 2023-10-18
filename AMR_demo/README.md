# Example Adaptive Mesh Refinement Runs

These runs are for exploring the physics-based AMR capabilities of
BATS-R-US.

The runs begin with two hours northward IMF before transition to a
storm-like state.  `imf_simple.dat` employs a simple, fast southward
turning of magnitude 10nT.  `imf_by.dat` includes a gradual IMF By component
30 minutes after the initial southward turning.

To intialize the run, first use `PARAM.in_amr_init`.
This will run the first two hours of the simulation *without* AMR turned on.
Then, choose the restart PARAM that is associated with the associated IMF file
you wish to use; change the `#SOLARWINDFILE` param as necessary to match the desired IMF file.
Check output frequencies and types in the `#SAVEPLOT` command.
On restart, the rest of the event is executed with AMR refining on $J^2$.

## Simulation Variations

| IMF File | PARAMs | Description |
|----------|--------|-------------|
| imf_simple.dat | PARAM.in_amr_init/_restart | Simple southward turning |
| imf_by.dat | PARAM.in_amr_init/PARAM.in_amrBy_restart | Simple southward turning followed by additional By component |
| imf_smallby.dat |  PARAM.in_amr_init/_restart | Simple southward turning with constant By (change #SOLARWINDFILE param) |

