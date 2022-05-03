# LWS GMD Param Files

These files are for the NASA Living With a Star GeoMagnetic Disturbance project, led by Dr. Yue Deng. The goal is to investigate the role of the thermosphere in creating and modulating the formation of ground magnetic signatures.

## Idealized Benchmark Simulations
The basic idealized input files run the SWMF/Geospace model without GITM to create a set of drivers for GITM stand-alone.

Information on simulations:
1.	Resolution of GITM runs: 1 deg lat x 1 deg lon. Output every 5 second to provide time series of dB to Steve.
2.	Equinox condition and seasonal effect in future maybe. (F10.7=150 s.f.u.)
3.	5-hour simulation, 1-hour quiet, 3-hour active, 1-hour recovery; Step function for forcing changes
4.	SW Pressure=1.6726e-6*n*v^2, n in /cc, v in km/s, SWP=1 nPa, n=3.7367~=3.74
5.	GITM runs of Run00, Run10, and Run30 have been completed.

The run numbers correspond to different solar driving conditions, given in the table below.

| Run # | $V$ ($km/s$) | $P$ ($nPa$) | $\rho$ ($1/cc$) | $B_Y$ ($nT$) | $B_Z$ ($nT$) |
|-------|-------------------|------------------|------------------|--------------|-------------|
| Run 00 | 400 | 1 | 3.74 | 0 | -1 |
| Run 01 | 400 | 1 | 3.74 | 0 | -1 $\rightarrow$ -20 |
| Run 02 | 400 | 1 $\rightarrow$ 5 | 3.74 $\rightarrow$ 18.68| 0 | -1 $\rightarrow$ -20 |
| Run 03 | 400 $\rightarrow$ 800 | 1 $\rightarrow$ 5 | 3.74 $\rightarrow$ 4.67  |0 | -1 $\rightarrow$ -20 |
| Run 04 | 400 $\rightarrow$ 800 km/s |1 $\rightarrow$ 5 | 3.74 $\rightarrow$ 4.67 | 0 $\rightarrow$ 10 | -1 $\rightarrow$ -20|
