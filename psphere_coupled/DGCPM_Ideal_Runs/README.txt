This is the basic multifluid simulation for looking at plasma plumes in
the GM magnetosphere. The PARAM files are the same used in our original simulation
on the this topic taken from the TACC repository:
This folder contains IMF data for four ideal runs.

1. imf_mf_bzturn_by.dat is an ideal square wave event
2. imf_cir_katus.dat    is an idealized corotating interaction region event
3. imf_cmemc_katus.dat  is an idealized coronal mass ejection magnetic cloud event
4. imf_cmesh_katus.dat  is an idealized coronal mass ejection sheath driven event

To change which storm is being simulated the #UPSTREAM_INPUT_FILE command in both
the PARAM.in.ss and PARAM.in.ta files needs to be changed.

VirtSats and sat.include contain the information needed to fly a large number of
virtual THEMIS and CLUSTER satellites s.t. 15 minutes after a virt sat flies
though a point in space another satellite will pass again. Thus along the orbital
path of the satellites there is no spot which goes more then 15 minutes without
being sampled. The orbits were taken from actual THEMIS and CLUSTER orbits over a
24 hour period. There is a jump in the orbit as a satellite begins the path over
again, but this jump has been placed so that it happens upstream of the earth.

SWMF Configuration:
Config.pl -install=BATSRUS,Ridley_serial,DGCPM [-compiler=...]
Config.pl -v=GM/BATSRUS,IE/Ridley_serial,PS/DGCPM
Config.pl -o=GM:e=MultiSwIono
