#ECHO
T

#DESCRIPTION
OutflowStandardStorm (OSS) - In the pipes +18hrs.

#TIMEACCURATE
F                       DoTimeAccurate

#IDEALAXES

#STARTTIME
2000            year
09              month
21              day
18              hour
00              minute
00              second
0.0             FracSecond

#COMPONENT
IM                      NameComp
F                       UseComp

#COMPONENT
PW
F

#COUPLE2
GM                      NameComp1
IE                      NameComp2
10                      DnCouple
-1.0                    DtCouple

#BEGIN_COMP GM ---------------------------------------------------------------

#INCLUDE
PARAM.gm.1st.superhi

#UPSTREAM_INPUT_FILE
T                       UseUpstreamInputFile
imf_stand.dat           UpstreamFileName
0.0                     Satellite_Y_Pos
0.0                     Satellite_Z_Pos

#END_COMP GM -----------------------------------------------------------------

#BEGIN_COMP IE ---------------------------------------------------------------

#IONOSPHERE
5                       TypeConductanceModel
F                       UseFullCurrent
F                       UseFakeRegion2
200.0                   F107Flux
1.0                     StarLightPedConductance
0.25                    PolarCapPedConductance

#SAVEPLOT
1                       nPlotFile
min idl                 StringPlot
100                     DnSavePlot
-1.0                    DtSavePlot

#SPS
T

#DEBUG
0
0

#END_COMP IE -----------------------------------------------------------------

#STOP
2000                     MaxIter
-1.                     TimeMax

#RUN    ######################################################################

#BEGIN_COMP GM ---------------------------------------------------------------

#INCLUDE
PARAM.gm.2nd

#END_COMP GM -----------------------------------------------------------------

#STOP
8000                    MaxIter
-1.                     TimeMax
