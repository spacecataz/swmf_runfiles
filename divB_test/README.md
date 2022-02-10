#Divergence of B Tests

These input files are for a project led by George Mason University to test
the ability of BATS-R-US to maintain $\nabla \overline B = 0$.

## Idealized Test
The folder `ideal_btest` contains a basic, high-resolution test of the
code.  IMF conditions begin purely northward at +5nT, then turn southward
to -10nT.  All other solar wind conditions are held constant.

Two sets of PARAMs are included: one *with* the Rice Convection Model ring current model (RCM, file suffix `_RCM.in`) and one without.

Configuration notes:

- Inputs are based on the CUSIA standard SWMF configuration.
- IE is using the standard Ridley Legacy Model for conductance with the advanced auroral oval specification.
- Output magnetometers are ONLY 5x5 degree global magnetometer grid coverage.