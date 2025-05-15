# Point-Source Simulations

This directory contains a set of inputs and tools for producing simulations
that have a point-source of mass density.

## Configuring the SWMF
To configure the SWMF, start by placing `ModUserPointSource.f90` into the
`srcUser` directory of BATS-R-US. Installation and configuration then
follows:

```
./Config.pl -install=BATSRUS,Ridley_serial,RCM2 -compiler=gfortran
./Config.pl -v=GM/BATSRUS,IM/RCM2,IE/Ridley_serial
./Config.pl -o=GM:u=PointSource

make SWMF PIDL
```

If you need to change `ModUserPointSource.f90`, you need re-execute the
User file command through `Config.pl` before recompiling.

## Using the User Module
The main command is `#POINTMASSSOURCE`, which works as follows:

```
#POINTMASSSOURCE
T         UsePointSource
360.      RateRotate [degrees/day]
1         nPointSource
100.0     SourceAmplitude (AMU/cm^3/s)
6.6       xPosition
0.0       yPosition
0.0       zPosition
```

If RateRotate is non-zero, spacecraft will rotate counter-clockwise about the
z-axis. This is useful for setting geosynchronous spacecraft in the equatorial
plane (RateRotate=360.).

All sources can be time activated by setting `#POINTSTART` and `#POINTSTOP`.
If either is not set, the corresponding start/stop time is not used.
The commands work like `#STARTTIME`:

```
#POINTSTART
2000			iYear
   3			iMonth
  21			iDay
  10			iHour
  45			iMinute
   0			iSecond
   0.0			FracSecond
```



## List of PARAM files:

| PARAM | Info |
|-------|------|
| PARAM.in_test | A single-CPU viable 2 minute test of the module. |
| PARAM.in_UserRef | Reference file for comparison to a different User file. |
| PARAM.in_SWPC_v2_init | Simple event simulation case for early simulation exercises. |
| PARAM.in_SWPC_extr_init | SWPC configured for an extreme event (1/100 year) |
| PARAM.in_SWPC_gannon_init | SWPC configured for the Gannon 2024 event. |

Note that the Gannon event requires `magin_GEM.dat` from the common file directory.
