#ECHO
T

#DESCRIPTION
Ideal run for southward IMF, 450km/s solar wind

#TIMEACCURATE
F			DoTimeAccurate

#STARTTIME
2000     year
01       month
01       day
06       hour
00       minute
00       second
0.0      FracSecond


#IDEALAXES

! No IM until time accurate.
#COMPONENT
IM			NameComp
F			UseComp

#COUPLE2
GM			NameComp1
IE			NameComp2
10                      DnCouple
-1.0                    DtCouple

#SAVERESTART
T
1000
-1

#BEGIN_COMP GM ---------------------------------------------------------------

#INCLUDE
PARAM.gm.1st.hires

#UPSTREAM_INPUT_FILE
T                       UseUpstreamInputFile
imf_cmesh_katus.dat     UpstreamFileName
0.0                     Satellite_Y_Pos
0.0                     Satellite_Z_Pos

#END_COMP GM -----------------------------------------------------------------

#BEGIN_COMP IE ---------------------------------------------------------------

#IONOSPHERE
5                       TypeConductanceModel
F                       UseFullCurrent
F			UseFakeRegion2
150.0                   F107Flux
1.0                     StarLightPedConductance
0.25                    PolarCapPedConductance

#CONDUCTANCEFILES
cmee_hal_coeffs.dat	NameHalFile
cmee_ped_coeffs.dat 	NamePedFile

#AURORALOVAL
T			UseOval (rest of parameters read if true)
T			UseOvalShift
F			UseSubOvalConductance
T			UseAdvancedOval
F			DoFitCircle (read if UseAdvancedOval is true)

#USECMEE
T			UseCMEEFitting (rest of parameters read if true)
45 			LatNoConductanceSI (default)
7.5 			FactorHallCMEE (default)
5 			FactorPedCMEE (default)


#BOUNDARY
10.0			LatBoundary

SPS
T

#DEBUG
0
0
#END_COMP IE -----------------------------------------------------------------

#STOP
1000                     MaxIter
-1.			TimeMax

#RUN	######################################################################

#BEGIN_COMP GM ---------------------------------------------------------------

#AMR
-1			DnRefine

#SCHEME
2			nORDER
Rusanov			TypeFlux
mc3                     TypeLimiter
1.2

#TIMESTEPPING
1			nStage
0.60			CflExlp

#BORIS
T
0.02

#END_COMP GM -----------------------------------------------------------------

#STOP
5000                    MaxIter
-1.			TimeMax

#END
