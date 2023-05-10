# Nov. 2001 Event Simulation

This simulation covers the Nov. 2001 strong storm event with applications to
the New Zealand power grid.

## Data
Upstream data is limited for this event. ACE SWEPAM did not operate normally.
The file `ACE_raw_2001308.dat` contains search-mode data.

Notes on this data from the provider:

As usual, the issue is that the instrument is measuring in the wrong energy range, due to the high charged particle background and the “special” way the instrument operates. This means that the only data from which moments can be calculated are from the so-called “Search” mode (aka STI mode), run about once every half hour, in which measurements are made over (nearly) the full instrument energy range with reduced resolution. Because the STI mode data have lower resolution and thus moments calculated from these data have higher uncertainties, they are not included in the validated Level 2 data set. However, the data are acceptable for scientific analysis, and should be fine for your purposes.

The attached data file (ascii text file) includes data from both the nominal (“Track”, SWI) and Search (STI) modes. Parameters are described at the top of the file, along with some caveats about the data. I note that the file includes B field measurements, but at the same 64-sec cadence as the plasma data. So the B fields here are good enough for a quick look, but you should get the higher resolution data from the magnetometer team for any real scientific analysis.