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