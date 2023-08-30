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
The #PLANE command can be optionally put in a solar wind input file for
running the SWMF, after the header with the names of the solar wind
parameters and before the time series of the parameters themselves. The
incoming solar wind front can be tilted in both the XY plane and the XZ
plane. The accompanying #POSITION command sets the origin of the tilt. 


The angles are oriented such that 0 is an unchanged front, the default
behavior. The angle set is with respect to the axis perpendicular to X;
e.g. for a 30^o^ angle in the XZ plane, the solar wind front enters
the grid at a 30^o^ from the positive Z edge of the grid. Setting the
angle to any multiple of 90^o^ will result in an unchanged front
parallel to the axis. Using angles greater than 180^o^ will have the
same results as setting $\theta$ - 180^o^.

In idealized runs, it is best to allow the simulation to run for a
short while before introducing a discontinuity in the solar wind; ten
to fifteen minutes of solar wind beforehand should be sufficient. This
will prevent part of the plane from being flattened (no tilt). A similar
option is to set the origin to the top (if the angle is less than
90^o^) or the bottom (if the angle is greater than 90^o^) of the grid
in the plane of the tilt.

Note: the #PLANE command merely changes the shape of the incoming
solar wind front, it does not actually rotate anything in the solar wind.
For example, a Ux with a 45^o^ tilt will still be a Ux, and setting
the angle to 180^o^ will not reverse the IMF Bz component.