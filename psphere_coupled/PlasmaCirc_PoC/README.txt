This is the basic multifluid simulation for looking at plasma plumes in
the GM magnetosphere.  IMF is northward for 8 hours, then southward for 8.

SWMF Configuration:
Config.pl -install=BATSRUS,Ridley_serial [-compiler=...]
Config.pl -v=GM/BATSRUS,IE/Ridley_serial
Config.pl -o=GM:e=MultiSwIono

Don't forget your test satellites!

To control the IM plasmasphere, edit the #MAGNETOSPHERE and #POLARBOUNDARY
params in PARAM.gm.1st.hires file and PARAM.in.ta file.  Setting
Fluid #2 to very low inner boundary values will "shut off" the
plume.  A value of 5/cc worked well in the past.

Updates:
2018-11-20 -- Added #AURORALOVAL command to fix CPCP oscillations.
              Added ray trace output files to MHD output.
	      Moved directory to "psphere_coupled".
