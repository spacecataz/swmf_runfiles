# Point-Source Simulations

This directory contains a set of inputs and tools for producing simulations
that have a point-source of mass density.

## Configuring the SWMF
To configure the SWMF, start by placing `ModUserPointSource.f90` into the
`srcUser` directory of BATS-R-US. Installation and configuration then
follows:

```
./Config.pl -install=BATSRUS,Ridley_serial,RCM2
./Config.pl -v=GM/BATSRUS,IM/RCM2,IE/Ridley_serial

make SWMF PIDL
```