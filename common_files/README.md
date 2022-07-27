This folder is for files that are common across all simulations.
They do not depend on time, event, or conditions.  An example is
magnetometer locations, which are constant over many simulations.

Files:

**mags_all.dat**
A comprehensive list of ground mangetometer stations and the geographic
coordinates.  Acts as input for the SWMF to produce virtual stations at
each real station location.  Includes all magnetometers listed on SuperMag,
Image, and others.

Duplicate mags:
Some magnetometers have repeat entries:
M87 is the same as B21.
M89 is the same as B22.
M85/86 is the same as B20/19.

**test_sats**
test_sats contains an include file and several virtual satellite input files
for stationary stats that probe different points within the magnetosphere.
Often useful for idealized runs, these satellites can be included in a
simulation by copying the folder into the run directory and using this
syntax within a `GM` section of a PARAM.in:

```
#INCLUDE
test_sats/test_sats.include
```