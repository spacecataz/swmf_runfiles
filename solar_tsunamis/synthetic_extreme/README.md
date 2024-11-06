# Synthetic Extremes for Solar Tsunamis

This directory contains run files for synthetic extreme event studies.

## Model Setup & Code Configuration

```
git clone git@github.com:SWMFsoftware/SWMF.git

./Config.pl -install=BATSRUS,RCM2,Ridley_serial -compiler=[YOUR CHOICE]
./Config.pl -v=GM/BATSRUS,IE/Ridley_serial,IM/RCM2
./Config.pl -o=IE:g=181,361
```

## Description of Extreme Scalings
Each scaling uses a set of hyperbolic tangents to ramp up then down the
amplitudes of storms within a given window.

### Tsurutani & Lahkina


### Gopalswamy

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
|imf_TS2014_KatusMedian.dat  | Same as above, but ML-based scaling for density, temperature amplitudes. |
|imf_unscaled_nt_model.dat | Random-forest recreation of Katus using Katus Bz, Vx |
|imf_scaled_nt_model.dat | Random-forest extreme event using TS-Katus Bz, Vx |