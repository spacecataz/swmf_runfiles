# Example Adaptive Mesh Refinement Runs

These runs are for exploring the physics-based AMR capabilities of
BATS-R-US.

The runs begin with two hours northward IMF before transition to a
storm-like state.  `imf_simple.dat` employs a simple, fast southward
turning of magnitude 10nT.  `imf_by.dat` includes a gradual IMF By component
30 minutes after the initial southward turning.

To intialize the run, first use `PARAM.in_amr_init`.
Then, choose the PARAM that is associated with the associated IMF file
you wish to use.