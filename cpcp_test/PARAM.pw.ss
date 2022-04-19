#ECHO
T

#TEST
get_HPI

#DESCRIPTION
PW steady state run.

#TIMEACCURATE
T                       DoTimeAccurate

#STARTTIME
2000            year
01              month
01              day
00              hour
00              minute
00              second
0.0             FracSecond

#IDEALAXES

#SAVERESTART
T
-1
3600

#COMPONENT
IM
F

#COMPONENT
GM
F

#COMPONENT
IE
F

#COMPONENT
PW
T

#BEGIN_COMP PW ######################################
#ROTATION
F		IsCentrifugal

#SCHEME
Godunov         TypeSolver
Godunov         TypeFlux
0.005           DtVertical
F               IsFullyImplicit
F               IsPointImplicit
F               IsPointImplicitAll

#MOTION
F		DoMove

#FIELDLINE
125		nTotalLine

#AURORA
T		UseAurora

#NGDC_INDICES
ApIndex.dat	NameNgdcFile
f107.txt	NameNgdcFile

#NOAAHPI_INDICES
power.txt	NameHpiFile

#MHD_INDICES
imf_pwss.dat	UpstreamFile

#SAVEPLOTELECTRODYNAMICS
T		DoPlotElectrodynamics
3600.0		DtPlotElectrodynamics

#SAVEPLOT
-1		DnSavePlot
3600		DtSavePlot
T		SaveFirst

#TYPEPLOT
real8		TypePlot

#END_COMP PW #######################

#STOP
-1		Tmax
86400		MaxStep
