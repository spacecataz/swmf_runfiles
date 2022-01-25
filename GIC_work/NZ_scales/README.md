# NZ GMD Scale Investigations

These input files are designed to investigate the spatial and temporal scales
of GMDs over the New Zealand land mass over a range of storm inputs.

Inputs are based on the *Katus et al. * SEA analysis, scaled up for extreme
storms.

PARAMs are based on the CUSIA Phase 1 idealized events.

## New Zealand Location & Magnetometer Placement
The main New Zealand islands span ~34 to 47 south latitude, centered about 172 east longitude.
Magnetic latitudes are ~3 degrees lower; AAGCM latitudes are ~7 degrees lower.

For this study, virtual magnetometers are placed from 60 to 25 south latitude about all geographic longitudes.
This allows for a

## Storm Configurations
At present, there are 2 storm configurations.  The PARAM files are currently set
to do the first. F10.7 values are educated guesses.

|Storm              | IMF File     | F10.7 |
|-------------------|--------------|-------|
|CME/Sheath Default | imf_SH.dat   | 200.0 |
|CME/Sheath x5      | imf_SH_5x.dat| 300.0 |

## Code setup and compilation
