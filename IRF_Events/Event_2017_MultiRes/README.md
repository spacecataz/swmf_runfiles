Resolution/Numerics Comparison Params
=====================================

These params are for comparing resolution and numerics in BATS.
SWPC versions are now legacy; do not use except for reference.

Notes
-----

ISSUES WITH VIRTUAL MAGS: on some machines, the number of virt mags that
are used here causes issues and unexplained crashes. If this occurs,
turn down the number of magnetometers in the #MAGNETOMETERGRID command
or lower the number of stations in `mags.out`.

Updates
-------

2021 - 11 - 01:

 + Moved all conservative criteria from TA to SS portion for GM.

2022 - 11 - 28:

 + Added files for MAGNIT conductance simulations.
 + Updated restart PARAM file to add additional output.