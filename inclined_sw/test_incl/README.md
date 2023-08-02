# Test Inclined Shock Fronts

This simulation set is for testing the functionality of the following
directives in IMF files on SWMF/Geospace simulations:

```
#PLANE The input data represents values on a tilted plane
0.0    	  Angle to rotate in the XY plane [deg]
30.0   	  Angle to rotate in the XZ plane [deg]

#POSITION Y-Z Position of the satellite (also origin of plane rotation)
0.0 	  Y location
0.0 	  Z location
```

The test is configured to be run on a local machine very quickly.

**The goal of this test is to better understand how the parameters of
`#PLANE` set the shock angle in GM.**

## Code Configuration
The simplest approach is to just call the SWPC test and use the resulting
run directory:

`make test_swpc`

## PARAM Notes
The PARAM is based on the Version 1 SWPC configuration with a few changes:

- Moved `#NONCONSERVATIVE` to prevent crashes.
- Turned off RB.
- Lowered steady state iterations
- Configured LAYOUT for desktop/serial use.
- 1 minute 2D slice output
- Turned off other output.

## Results:
When we figure things out, we'll make notes here.