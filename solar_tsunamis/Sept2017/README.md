# Solar Tsunami Event Runs

These runs are for the University of Otago Solar Tsunamis, the September 2017 event.
Some are high spatial resolution and extreme high resolution for output.
Others (`PARAM.in_*_lowres`) are standard configurations similar to the SWPC v2 configuration.

**Note special Config.pl options to meet simulation demands.**

## Solar wind drivers
There are 12 sets of solar wind drivers for the Sept 2017 run:

- `IMF_advected.dat`, which is ACE observations advected to the approximate nose of the bowshock using MHD results (NOTE: check with S. Morley to confirm propagation/processing method). One minute time resolution.
- `IMF_omni.dat`, which is data taken directly from OMNIWeb and contains clear propagation issues, esp. at shock arrival (x2). One minute time resolution.
- `IMF_{wind, ace, or dscovr}.dat`, which are ACE, Wind, or DSCOVR observations
ballistically propagated to the upstream simulation boundary. One minute time resolution.
- `IMF_{wind, ace, or dscovr}_mhdprop.dat`, which are ACE, Wind, or DSCOVR observations
propagated to the upstream simulation boundary by a 1D MHD propagation. One minute time resolution.
- `IMF_ace_mhdprop_1s.dat`, which is ACE observations at a 1s cadence
propagated to the upstream simulation boundary by a 1D MHD propagation.
- `IMF_ace_20170906_175000_merged_tshift25.dat`, which is unpropagated ACE observations with the time array shifted forward by 25 minutes. One minute time resolution.
- `IMF_dscovr_20170906_175700_merged_tshift32.dat`, which is unpropagated Wind observations with the time array shifted forward by 32 minutes. One minute time resolution.
- `IMF_wind_20170906_175800_merged_tshift33.dat`, which is unpropagated Wind observations with the time array shifted forward by 33 minutes. One minute time resolution.



## Configurations

The runs can be configured 6 ways:

| PARAM suffix | Conductance  | GITM Coupling? |
|--------------|--------------|----------------|
| `*_rlm`      | Ridley Legacy| No  |
| `*_cmee`     | CMEE         | No  |
| `*_rlm_ua`   | Ridley Legacy| Yes |

### Configuring with Config.pl

Note some non-standard items, e.g., double res for Ridley_serial.


**For RLM runs:**

```
./Config.pl -install=BATSRUS,RCM2,Ridley_serial -compiler=[YOUR CHOICE]
./Config.pl -v=GM/BATSRUS,IE/Ridley_serial,IM/RCM2
./Config.pl -o=IE:g=181,361
make
```