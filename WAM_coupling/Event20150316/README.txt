Everyone wants to simulate the "St. Patrick's Day" storm of March 17, 2015.
Rather than distribute files across many folders, let's consolodate those
events in one spot.

Input Value Description
-----------------------
IMF values were obtained via ACE MFI from CDAWeb.
Solar wind plasma parameters were obtained from ACE SWEPAM via CDAWeb.
Values were propagated via Aaron Ridley's IDL cdf_to_mhd routine.
Significant gaps exist in SWEPAM density.  These values were suplemented
via OMNI database values.  The OMNI propagation matches very well with
the Ridley ballistic method.

F10.7 value (115 SFU) was obtained from this website:
http://www.spaceweather.gc.ca/solarflux/sx-5-flux-en.php?year=2015

Param File Description
----------------------
PARAM.in_SWPC and PARAM.in_SWPC_hires: default SWPC configuration with some
minor changes (output type and frequency, removal of real-time options, etc.)
Notable changes are outputs relevant to LWS work for IE.

PARAM.in_ExHail uses 8M cells, no IM component, and ideal axes..
The goal is to output many shell slices to see how DeFacto outflow varies
throughout the storm for ExHail reconstructions. CPCPBOUNDARY is turned off.
