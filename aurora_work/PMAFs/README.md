# PMAF Simulations

**P**oleward **M**oving **A**uroral **F**orms are dayside auroral features
associated with the onset of reconnection.

The files in this folder are for running PMAF simulations with the SWMF.

## SWMF Install & Configuration

For the "base" SWMF, install and configure with SWPC_v2
settings (with higher resolution IE at 181 lats, 361 lons)

```
./Config.pl -install=BATSRUS,RCM2,Ridley_serial
./Config.pl -v=GM/BATSRUS,IE/Ridley_serial,IM/RCM2
./Config.pl -o=IE:g=181,361
```

Installing GITM stand-alone:
```
git clone git@github.com:GITMCode/GITM.git
./Config.pl -install -earth -compiler=[compliler name here]
make
```

Installing SWMF with GITM:
```
# From the SWMF install directory, bring in GITM.
cd UA/
git clone git@github.com:GITMCode/GITM.git
cd GITM
git switch SWMF
cd ../..

# Configure and install the SWMF with GITM:
./Config.pl -install= -compiler=[compiler name here]
./Config.pl -v=GM/BATSRUS,IE/Ridley_serial,IM/RCM2,UA/GITM
./Config.pl -o=IE:g=181,361
```


## Input Files & Events

The `PARAM.in` naming convention for events is,

`PARAM.in.<config>_<eventdate>`

...where `eventdate` should be `YYYYMMDD` and `config` should express the
model configuration (e.g., `GITMmagnit` for GITM and MAGNIT use).

The `imf*.dat` naming convention is,

`imf_<source>_<event>.dat`

...where `eventdate` should be `YYYYMMDD` and `source` should be omni, wind,
ace, or dscovr.

PARAM files include are named `PARAM.in_<RUN>_<STAGE>`

- RUN: Components included (e.g., GMIMIE or GMIMIEUA)
- STAGE: `init` (start from steady state up to event time) vs. `restart` (continue up to event time) vs. `event`(restart at event time with high cadence output).

## PMAF Events

For each event, there are 3 start times:
- **GITM Start**: 24 hours of time to wind up GITM to a
realistic solution.
- **SWMF Start**: At least 8 hours before the PMAF event.
- **Event Start**: The time the PMAF begins
The simulation is run for **2 hours** from the event start.

PARAM files are set up for the Dec. 18th event by default.
Change the start time and IMF file to customize for other events.
If spacecraft orbit files are available, add the contents of the `sats.include`
file to the PARAM input.

#### Dec. 18th, 2017

| GITM Start Time  | SWMF Start Time  | Event Start Time |
|------------------|------------------|------------------|
| 2017-12-16 23:30 | 2017-12-17 23:30 | 2017-12-18 07:30 |

**Recommended Input: WIND** Wind has fewer plasma data gaps.
During the event, IMF is predominantly southward; with ACE,
there are short northward turnings.

This is a well-studied and text-book PMAF event. Details of this event can
be found in the following publication:
> Fasel, G. J., Lee, L. C., Lake, E., Csonge, D., Yonano, B., Bradley, O., et al. (2024). Correlation between the solar wind speed and the passage of poleward-moving auroral forms into the polar cap. Frontiers in Astronomy and Space Sciences, 10. https://doi.org/10.3389/fspas.2023.1233060


#### Jan. 3rd, 2020

| GITM Start Time  | SWMF Start Time  | Event Start Time |
|------------------|------------------|------------------|
| 2020-01-02 00:30 | 2020-01-03 00:30 | 2020-01-03 08:30 |

**Recommended Input: WIND** ACE data has no density information.

This event occurs during especially strong IMF B$_Y$ and creates a poleward
"flow" of aurora that is unique compared to typical PMAFs.

## GITM Info
Most of the tips & instructions are in the UAM file. There's a python command you can use to download the input IMF & AE data. This file will use FTA & weimer for aurora & potentials.

things you'll need to change:
- start/end dates, duh
- resolution, unless debugging
- outputs?
- input files: IMF (mhd_indices), sme (sme_indices)
- Fism year. File should be included in run/ already

Some links:
- more grid discussion: https://gitm.readthedocs.io/en/stable/common_inputs/#setting-the-grid
- outputs: https://gitm.readthedocs.io/en/stable/outputs/
    - the postprocess discussion is too new. On the swmf branch there is no post_process.py. Either get it (& pGITM.py) or just call ./pGITM over & over again


Install instructions should be the same for swmf & main branch, except for specifying compiler when you ./Config.pl
> use compiler=gfortran10 for versions 10+
> compiler=gfortran for less than 9
> compiler=intel or compiler=ifortmpif90 for intel. Depends on the machine