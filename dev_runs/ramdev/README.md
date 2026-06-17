# RAM-SCB Development PARAMs

This folder contains PARAMs and input files for establishing and testing
coupling between the SWMF and RAM-SCB

### Installation & Configuration

```
./Config.pl -install= -compiler=gfortran  # ...or best compiler choice here!
./Config.pl -v=IM/RAM_SCB,GM/BATSRUS,IE/Ridley_serial
```

For higher resolution and science grade runs, turn up the resolution in
RIM/Ridley_serial via:

```
/Config.pl -o=IE:g=181,361
```

### Runfiles

| PARAM File      | Description |
|----------------------|-------------|
|PARAM.in_testing      | Very simple, single-node testing at very low resolution. |
|PARAM.in_SWPC_init    | SWPCv2-like configuration for med. res science runs.     |
|PARAM.in_SWPC_restart | ...and the restart file for restarting.                  |
