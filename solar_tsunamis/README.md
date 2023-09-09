# Solar Tsunami Event Runs

These runs are for the University of Otago Solar Tsunamis event. They are
high spatial resolution and extreme high resolution for output.

**Note special Config.pl options to meet simulation demands.**

## Events

7 Sept 2017

## Solar wind drivers
There are two sets of solar wind drivers for the Sept 2017 run:

- `IMF_advected.dat`, which is ACE observations advected to the approximate nose of the bowshock using MHD results (NOTE: check with S. Morley to confirm propagation/processing method).
- `IMF_omni.dat`, which is data taken directly from OMNIWeb and contains clear propagation issues, esp. at shock arrival (x2).

## Configurations

The runs can be configured 6 ways:

| PARAM suffix | Conductance  | GITM Coupling? |
|--------------|--------------|----------------|
| `*_rlm`      | Ridley Legacy| No |
| `*_cmee`     | CMEE         | No |
| `*_magnit`   |
| `*_rlm_gitm` |

### Configuring with Config.pl

Note some non-standard items, e.g., double res for Ridley_serial.


**For RLM runs:**

```
./Config.pl -install=BATSRUS,RCM2,Ridley_serial -compiler=[YOUR CHOICE]
./Config.pl -v=GM/BATSRUS,IE/Ridley_serial,IM/RCM2
./Config.pl -o=IE:g=181,361
make
```