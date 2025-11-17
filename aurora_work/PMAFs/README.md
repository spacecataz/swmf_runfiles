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

## Events

For each event, there are 3 start times:
- **GITM Start**: 24 hours of time to wind up GITM to a
realistic solution.
- **SWMF Start**: At least 8 hours before the PMAF event.
- **Event Start**: The time the PMAF begins
The simulation is run for **2 hours** from the event start.

PARAM files are set up for the Dec. 18th event by default.
Change the start time and IMF file to customize for other events.

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