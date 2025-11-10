# PMAF Simulations

**P**oleward **M**oving **A**uroral **F**orms are dayside auroral features
associated with the onset of reconnection.

The files in this folder are for running PMAF simulations with the SWMF.

## SWMF Install & Configuration

## Input Files & Events

The `PARAM.in` naming convention for events is,

`PARAM.in.<config>_<eventdate>`

...where `eventdate` should be `YYYYMMDD` and `config` should express the
model configuration (e.g., `GITMmagnit` for GITM and MAGNIT use).

The `imf*.dat` naming convention is,

`imf_<source>_<event>.dat`

...where `eventdate` should be `YYYYMMDD` and `source` should be omni, wind,
ace, or dscovr.

## Events
#### Dec. 18th, 2017
This is a well-studied and text-book PMAF event. Details of this event can
be found in the following publication:
> Fasel, G. J., Lee, L. C., Lake, E., Csonge, D., Yonano, B., Bradley, O., et al. (2024). Correlation between the solar wind speed and the passage of poleward-moving auroral forms into the polar cap. Frontiers in Astronomy and Space Sciences, 10. https://doi.org/10.3389/fspas.2023.1233060


#### Jan. 3rd, 2020
This event occurs during especially strong IMF B$_Y$ and creates a poleward
"flow" of aurora that is unique compared to typical PMAFs.