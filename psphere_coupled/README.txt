These are simulations that couple PS/DGCPM to IE and GM.

PLASCIRC_POC
This is the proof-of-concept run to test if we can create psuedo-plumes
in multifluid BATS.  It uses #MAGNETOSPHERE and #POLARBOUNDARY to restrict
IB densities about the equator.  This grows into a plasmasphere that forms
a plume under southward IMF conditions.

PSGMIE_SIMPLE1WAY
This run is nearly the same as the PlasCirc_PoC runs in entryMF, but
GM is only single fluid and the IE potential is used to drive DGCPM.
Don't forget your test satellites!

PSGMIE_POC
This is the proof-of-concept simulation for PS->GM coupling.  It is the same
as PlasCirc_PoC except that PS is turned on and is coupling into one of
the GM fluids.
