This is the basic multifluid simulation for looking at plasma plumes in
the GM magnetosphere.  IMF is northward for 8 hours, then southward for 8.
To get a plume, coupling between PS and GM is used.

SWMF Configuration:
Config.pl -install=BATSRUS,Ridley_serial,DGCPM [-compiler=...]
Config.pl -v=GM/BATSRUS,IE/Ridley_serial,PS/DGCPM
Config.pl -o=GM:e=MultiSwIono

Don't forget your test satellites!

Slight differences between this and the "defacto plume" run:
Again, #MAGNETOSPHERE and #POLARBOUNDARY params are used to control the
fluids in the plasmasphere.  However, the density for Fluid  #2 at the
inner boundary is set down to 10 instead of 500.  Coupling handles the rest.
Further, the Polar Boundary density for fluid 2 is increased to 0.01 to
speed up the run a touch.

For testing purposes, there is now a PARAM.gm.1st.lowres.  This uses
the SWPC v1 grid and runs really fast.
