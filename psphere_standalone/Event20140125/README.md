# 2014 Jan. 25 Long-Lived-Plume Event

This is an extended High Speed Stream/Co-rotating Interaction Region event that produced one of the infamous "long lived plumes" that drained the plasmasphere for days on end.

`PARAM.in.ps` and `PARAM.in.psie` are configurations to simulate this event in support of the Long Lived Plume study.

`PARAM.in.ps_vistrack` is a configuration for simulating this event in support of development of an image-based machine learning algorithm for extracting velocity fields in the plasmasphere.

## VizPlas Configuration
For the vistrack simulation, source files must be updated to get the structure
in the plasmasphere required to test the visual tracking software.
The `*.f` and `*.f90` files in this directory should be put into the
`SWMF/PS/DGCPM/src/` directory before compilation.

Comipilation is a regular DGCPM install after that point.