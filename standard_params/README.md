The files in this directory represent the basic settings for the various SWMF configurations.
They have been tested for typical storm strengths, i.e., Galaxy15 through Gannon.
To use, follow the configuration instructions for each, change the start and end date/time
and the IMF file name, turn on your desired output, and copy the PARAM to PARAM.in in your
run directory.

**`PARAM.in_imp`**: The basic configuration with CIMI/IMP.
To configure the SWMF to work with this file, run `make_test_swpc_cimi`.
(Make sure the wave files have been copied over into the `IM` directory
from `SWMF_data/IM/CIMI/data`!)