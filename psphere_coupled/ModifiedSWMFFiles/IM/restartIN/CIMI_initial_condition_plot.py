"""
The prupose of this file is to plot the data in the file which CIMI uses to define its
intial plasmasphere density distrobution.
This file is called 'cimi_from_dgcpm_restart.dat' though other names descriptive of how the 
file has changed from the base line might be used. 
(typically of the form 'cimi_from_dgcpm_restart_XXX.dat')

In actual use of the cimi_from_dgcpm_restart.dat file it is placed in the run directory of the 
SWMF such that the path is RUNDIR/IM/restartIN/cimi_from_dgcpm_restart.dat
in its current ideration CIMI must have the file path be the above, any deviation leads to a crash.

Becuase of this many different density profiles are created all with the same file name. 
This script can take in a file, orginzed in the manner of the basic cimi_from_dgcpm_restart.dat 
file, and plot its density profile so that the user may see which density profile is 
actually being used. 

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
The file name which is plotted is hard coded on line 76 (the definitation of the variable 'data').
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

cimi_from_dgcpm_restart.dat reports the density in /m3 so divide by 1e6 to convert to the SWMF's 
/cm3 density (in output files, SWMF runs SI units during the actual simulation).
The CIMI grid has 76 (Lat), 48 (Lon) data points. Don't forget this array needs to
be ordered in a fortran way!
"""
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.ticker import MultipleLocator, LogLocator
from spacepy.pybats.dgcpm import _adjust_dialplot
import numpy as np

# Cimi's grid variable for ploting onto    
xlatCimideg = np.array([11.80942872141973,13.776618825031784,15.74173938132532,17.704530843111886,19.664767814148863,21.622108784977762,23.5762054159509,25.5266205749614,27.472807846875664,29.4141730052359,31.34988276696336,33.278963830101326,35.20014919455876,37.11178595455651,39.01168161937101,40.89679675482161,42.76286249267704,44.603509681536266,46.40889943389988,48.162758824070345,49.83685526511339,51.381509376100944,52.7245636235464,53.823076608137896,54.72001704994397,55.487573218302494,56.17547572056033,56.81199812478674,57.41343043215221,57.98966275657492,58.547088155118004,59.09003696771524,59.62157253420939,60.143938571742794,60.65882213704045,61.16754487170676,61.671144964495554,62.17047789660038,62.666224979390954,63.158977024230474,63.649244587759405,64.13745455680088,64.62399966723214,65.10922484360631,65.59345110481436,66.0769755640852,66.56009533464771,67.04307167123766,67.52618631915828,68.009715901071,68.49394386982635,68.97916904620051,69.46571415663179,69.95392583322055,70.4441882741076,70.9369437340417,71.43269252437958,71.93201862629523,72.4356255492732,72.94434999148679,73.45923526433174,73.98159959431786,74.51313345326471,75.05608397340924,75.61350766440503,76.18973998882774,76.79116802732499,77.42769726174056,78.1155980564511,78.88315678613057,79.780096374163,80.87860082101803,82.22165592223715,83.7663121676588,85.4404094624755,87.19427098708007])
CimiL = np.cos(xlatCimideg*np.pi/180.)**-2
phiCimideg=np.array([0.0,7.499999999999999,14.999999999999998,22.5,29.999999999999996,37.49999999999999,45.0,52.49999999999999,59.99999999999999,67.5,74.99999999999999,82.49999999999999,90.0,97.5,104.99999999999999,112.49999999999999,119.99999999999999,127.49999999999999,135.0,142.5,149.99999999999997,157.5,164.99999999999997,172.49999999999997,180.0,187.5,195.0,202.49999999999997,209.99999999999997,217.49999999999997,224.99999999999997,232.5,239.99999999999997,247.49999999999997,254.99999999999997,262.49999999999994,270.0,277.5,285.0,292.49999999999994,299.99999999999994,307.49999999999994,315.0,322.5,329.99999999999994,337.49999999999994,344.99999999999994,352.49999999999994])
# To aid with plotting we allow results to cross lon = 360
lon = np.concatenate( (phiCimideg, [360.0]) ) * np.pi/180. - np.pi/2.

def MakePlot(density):
    #Make a Plot to determine that things are done correctly. Should generate the Tear drop plasmasphere pointing
    #duskward.
    fig, ax1 = plt.subplots(subplot_kw=dict(projection='polar'))
    
    #create the fill values
    nLev = 51
    zlim = [density.min(), density.max()]
    levs = np.power(10, np.linspace(np.log10(zlim[0]), np.log10(zlim[1]), nLev))
    z=np.where(density>zlim[0],  density, 1.01*zlim[0])
    z[z>zlim[-1]] = zlim[-1] # If a z value is greater then the maximum, set it equal to the maximum.
    norm=LogNorm()
    lct= LogLocator()

    #allow results to cross lon = 360
    lon = np.concatenate( (phiCimideg, [360.0]) ) * np.pi/180. - np.pi/2.
    z = np.concatenate( (z, np.array([z[:,0]]).transpose()  ), 1)

    #plot away
    cont = ax1.contourf(lon, CimiL, z, levs, norm = norm, cmap = 'Greens_r')
    cbar = plt.colorbar(cont, pad=0.1, shrink=.9, ticks=lct, ax=ax1)
    cbar.set_label(r'Intial Density ($cm^{-3}$)')
    #cbar.set_ticks([1e-3,1e-2,1e-1,1,1e1,1e2,1e3])
    Lmax = 12 # Cimi's L techincally goes waaaaaay out, so we limit the plotting range here.
    _adjust_dialplot(ax1, Lmax, labelsize = 14)

    # This block adds a circle of radius ScaleR to the plot
    ScaleR = 6.6
    R = np.ones((len(lon),)) * ScaleR
    ax1.scatter(lon, R)

    plt.suptitle('Density of Initail DGCPM Restart Interpolated onto CIMI grid')
    plt.subplots_adjust(right=.95, left = .05, bottom = .1, top = .90)
    plt.show()

    return fig, plt, ax1, cont, cbar

data = open('cimi_from_dgcpm_restart_filtered.dat', 'r').readlines()

data[0] = data[0].split()
for i in range(len(data[0])):
    data[0][i] = float(data[0][i])

density = data[0]
density = np.array(density)
density = density / 1e6

density = np.reshape(density, (76,48), order = 'F')
density = np.roll(density, 24, axis = 1) # I had to roll the array to write the file intially. Not sure 
# why I need to roll it here but the following plot command makes it clear. With out the roll the tear drop 
# points dawnward when it should point duskward.
fig, plt, ax1, cont, cbar = MakePlot(density)
