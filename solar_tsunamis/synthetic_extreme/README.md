# Synthetic Extremes for Solar Tsunamis

This directory contains run files for synthetic extreme event studies.

## Model Setup & Code Configuration



## Run Configurations

PARAM setups are listed below with the following common settings:

- `#IDEALAXES` is used (magnetic axis aligned with rotation axis).
- `#MAGNETICINNERBOUNDARY` is set to `T` to help improve near-body field calculations under extreme conditions.
- MHD inner boundary is reduced to 1.75 with $R_{currents}$ set to 2.25 $R_E$.
- F10.7 flux is set to 255 SFU.
- All inter-model couplings are set to 5$s$.
- Magnetometer output is set to 20$s$.

| PARAM suffix | Description |
|--------------|-------------|
|init/restart | File is either an initialization or restart |
|SWPC          | SWPCv2-like configuration |

| IMF File | Description |
|--------------|-------------|
|imf_TS2014_KatusMedian.dat | Katus et al. SEA medians set to match Tsurutani & Lakhina, 2014 |
|SWPC          | SWPCv2-like configuration |