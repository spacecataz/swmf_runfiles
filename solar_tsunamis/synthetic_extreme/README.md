# Synthetic Extremes for Solar Tsunamis

This directory contains run files for synthetic extreme event studies.

## Description of ML/AI Generation
All machine-learning-based extreme specifications start by training on the
Katus et al. event list using CMEs with Sheaths.

### Random Forest Specifications
A random-forest based specification was created, first by Rashmi Siddalingappa
and then by Qusai Al-Shidi (both of WVU). The former was not able to create
a reasonable time series, but amplitudes were used to scale the SEA time series
(see below). The latter produced a time series useable here.

## Description of Extreme Scalings
Heuristically-scaled extremes begin with the Katus et al. SEA data (either
means or medians) which are then scaled up to amplitudes to match extreme
event scenarios in literature. Each scaling uses a set of hyperbolic tangents
to ramp up then down the amplitudes of storms within a given window.
Ramp up time is 15 minutes; ramp down is 12 hours.

### ML-Scaled
A random-forest based specification was created, first by Rashmi Siddalingappa
and then by Qusai Al-Shidi (both of WVU). The former was not able to create
a reasonable time series, so the amplitudes were used as an alternative to
other scalings, as described below. **This specification is not recommended.**

### Tsurutani & Lahkina Most Extreme SSI
Tsurutani & Lahkina calculations put the total solar wind velocity at just
under 2700$km/s$ and a total $B$-field of 128$nT$. $B$ is scaled by component
such that $|B|$ matches the T&L values. Number density is not scaled (T&S
specify a value of 20$/cc$, matching Katus et al. closely).

### Gopalswamy 1/100 and 1/1000-Year Estimates
Gopalswamy paper blah gives estimates for 1/100 and 1/1000 year events.
We take the 1/100 and 1/1000 values; slow the solar wind by 10%, and use
Equation 7 to get the associated total magnetic field.

The values are summarized below:

| Freq (1/yr)| Dist. Type | Max $V$    | Total $E$   | 90% $V_max$ | Max $B$ |
|------------|------------|------------|-------------|-------------|---------|
| 1/100      | Weibull    | 3800$km/s$ | 4.4E33$ergs |             |         |
| 1/1000     | Weibull    | 4700$km/s$ | 9.8E33$ergs |             |         |

- No slowdown from near-Sun to L1 velocity.

## Model Setup & Code Configuration

```
git clone git@github.com:SWMFsoftware/SWMF.git

./Config.pl -install=BATSRUS,RCM2,Ridley_serial -compiler=[YOUR CHOICE]
./Config.pl -v=GM/BATSRUS,IE/Ridley_serial,IM/RCM2
./Config.pl -o=IE:g=181,361
```

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
|imf_TS2014ML_KatusMedian.dat  | Same as above, but ML-based scaling for density, temperature amplitudes. |
|imf_unscaled_nt_model.dat | Random-forest recreation of Katus using Katus Bz, Vx |
|imf_scaled_nt_model.dat | Random-forest extreme event using TS-Katus Bz, Vx |