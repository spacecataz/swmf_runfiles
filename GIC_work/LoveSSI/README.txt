This is a simulation in response to a request from Jeff Love (USGS) to
investigate the effects of the storm SSI on ground based delta-B, dB/dt, and
GIC generation.  The solar wind inputs were originally created by Mike
Wiltberger who failed to get LFM to simulate the event.  These inputs
are created by Mike's IPython notebook file (LoveExtremeSW.ipynb) which has
been lightly edited to run without extra imports and create input for the
SWMF via Pybats.

F10.7 values selected from CWMM Oct. 2003 event values (255).

Don't forget those test satellites!  test_sats/test_sats.include

SWMF Setup: use the standard GM-IM-IE setup used for the SWPC selection runs.

UPDATE-----APRIL 2016: hiresR2 files are default!!!
Adopted inner boundary radius of 1.75
Increased IM and IE coupling frequency in restart param.

UPDATE-----MAY 2017: hiresR2 updated slightly.
New auororal oval implementation.
one-second maggrid output.
Dumping oval position information

UPDATE-----OCT 2018:
Added "amr" versions that use AMR before the shock to get the best results.

UPDATE-----SEPT 2019:
Added "low" and "superhi" resolution versions to investigate the effects
of resolution on FACs and dB/dt.  Mag list is now identical to that used by
the IRF events for collaboration with that team.
