# RAM-SCB Development PARAMs

This folder contains PARAMs and input files for establishing and testing
coupling between the SWMF and RAM-SCB

### Installation & Configuration

Activate required libraries **NOTE: SOLUTION STILL BEING DEVELOPED FOR ATHENA**

```
module load cray-netcdf/4.9.2.1
```

Check out the SWMF and RAM from their respective repositories.
Note that the SWMF-coupled RAM version is a dev branch on a fork from the main repo.
Further, as dashes in directory names are not well handled by the SWMF, rename `RAM-SCB` to `RAM_SCB`.
Be sure to place RAM-SCB into the `SWMF/IM` directory before installation.

```
git clone --depth 1 http://github.com/SWMFsoftware/SWMF.git
cd SWMF/IM
git clone git@github.com:patronus19/RAM-SCB.git
mv RAM-SCB RAM_SCB
cd RAM_SCB
git switch swmfdev
```

Next, configure as usual.

```
./Config.pl -install=BATSRUS,Ridley_serial -compiler=gfortran
./Config.pl -v=IM/RAM_SCB,GM/BATSRUS,IE/Ridley_serial
```

As always, choice of compiler is machine-specific. The `-compiler` flag should be omitted on NASA's Athena.

For higher resolution and science grade runs, turn up the resolution in RIM/Ridley_serial via:

```
./Config.pl -o=IE:g=181,361
```

...and compile as usual:

```
make SWMF PIDL rundir
```

### Runfiles

| PARAM File      | Description |
|----------------------|-------------|
|PARAM.in_testing      | Very simple, single-node testing at very low resolution. |
|PARAM.in_SWPC_init    | SWPCv2-like configuration for med. res science runs.     |
|PARAM.in_SWPC_restart | ...and the restart file for restarting.                  |
|PARAM.in_SWPC_init_RCM | SWPCv2, but with RCM for comparison's sake. |

