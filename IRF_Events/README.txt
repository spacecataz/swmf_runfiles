Simulation files for the IRF GIC collaboration.
SWPC files were changed as follows:

--Turned off all operational options (e.g., re-read IMF, etc.)
--Turned up virtual mag output to 10s resolution
--Updated mag list to be more comprehensive.
--Hourly restarts with no directory creation
--No RB component.
--60s 2D slice output
--72x32 mag grids
--AURORAOVAL used in both hi and low res.

Files at top level are "generic", files in individual directories are
event specific.

Two types of IMF are or will be added:
IMF.dat      - from OMNI or similar.
IMF_swmf.dat - from EEGL/AWSOM combination.
