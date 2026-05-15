# RECONNECTIONS - a folder of reconnection studies

This folder contains inputs for reconnection-focused studies.

## Comparing Reconnection Rates
`PARAM.in_compare_resistives` is an input file for comparing different
resistivity implementations: anomalous, Hall, uniform, and ideal MHD.
To switch modes, simply comment/uncomment the relevant lines in the
time accurate portion of the simulation.

This run is highly idealized: the IMF file is a simple southward turning with
constant flow conditions. Earth has no dipole tilt.

3D output is saved every 10 minutes for use in RECONEXUS.
