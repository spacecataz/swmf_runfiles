# SCALE UP!!!
Files for a series of runs with successively scaled-up inputs,
based on the original Gannon (May 2024) storm.

The research goal of these files is simple: How different is the ground
response for extreme events if...

1. ...we naively upscale the **ground response** by some multiple?
2. ...we naively upscale the **solar conditions** by some multiple?

The result will shed light on how we consider extreme event benchmarks for
GIC applications.

## Scaling Procedure
The scaling of the solar wind conditions uses the `SEA_drivers` files in
this repository and follows the procedure laid out in
`sample_scripts/gen_extreme2023.py`.
Rather than use more physically-motivated scalings, we use constant scaling
factors here. The point is not to be physically consistent; rather we are just
testing the impact of solar vs. ground response scaling.