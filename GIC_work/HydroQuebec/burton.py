#!/usr/bin/env python
'''
A module/script for applying the Burton equation to the July, 2000 superstorm.
'''

import numpy as np

# Some global constants.
eVcm3 = 0.01042446941323346 #convert pressure to eV/cm3
mVm   = 1.0E-3  # Convert nT*km/s to mV/m.

# The "burton constants":
aBurt = 3.6E-5
bBurt = 0.20
cBurt = 20.0
dBurt = -1.5E-3

def create_functions(imf):
    '''
    Given an IMF object, create and return functions for dP/dt, P, and
    F(E(t)), all required by the Burton equation.  These functions are
    valid for any time; linear interpolation is used to map values between
    discrete points.
    '''

    from scipy.interpolate import interp1d
    
    # Get a vector of time from the start of file, in seconds.
    t=np.array([ (x-imf['time'][0]).total_seconds() for x in imf['time']])
    
    # Get solar wind P in ev/cm-3; take square root.
    p = np.sqrt(eVcm3*imf['rho']*imf['ux']**2)

    # Get time derivative of sqrt(P)...
    dPdt = np.zeros(p.size)
    # ...using 2nd-order central differencing for center points...
    dPdt[1:-1] = (p[2:] - p[:-2]) / (t[2:]-t[:-2])
    # ...forward/backward differencing for first and last points.
    dPdt[0]  = (-3.*p[0]  + 4.*p[1]  - p[2] ) / (t[2]  - t[0] )
    dPdt[-1] = ( 3.*p[-1] - 4.*p[-2] + p[-3]) / (t[-1] - t[-3])

    # Create IMF E_y in mA/m.
    Ey = imf['bz']*imf['ux']*mVm
    # Convert to function F(E):
    LowE, BigE = Ey<0.5, Ey>=0.5
    Ey[LowE] = 0.0
    Ey[BigE] = dBurt*(Ey[BigE]-0.5)

    # For each value, create an interpolation function.
    p    = interp1d(t, p*aBurt*bBurt)
    dPdt = interp1d(t, dPdt*bBurt)
    F    = interp1d(t, Ey)

    return p, dPdt, F

def burton_euler(ImfFile, dT=300.0, DstStart=0.0):
    '''
    Given a Dst value at t=0 and an IMF input file, integrate the Burton
    equation over the period spanned by the IMF file and return a time
    vector and Dst.
    '''

    from spacepy.pybats import ImfInput
    from datetime import timedelta

    # Open the IMF file and calculate key values.
    imf = ImfInput(ImfFile)
    Psw, dPsw, Fe = create_functions(imf)

    # Now, use time range to build an array for Dst. 
    TimeStop = (imf['time'][-1] - imf['time'][0]).total_seconds()
    nPoints  = int(TimeStop/dT)
    dst = np.zeros(nPoints+1)
    dst[0] = DstStart

    # Integrate.
    for i in range(nPoints):
        tNow = i*dT
        dst[i+1] = dst[i] + dT*(
            -aBurt*dst[i] + Psw(tNow) - aBurt*cBurt + Fe(tNow) + dPsw(tNow))

    # Create a datetime array corresponding to integration times:
    time = [imf['time'][0] + timedelta(seconds=i*dT) for i in range(nPoints+1)]
    return time, dst


def burton_rk4(ImfFile, dT=300.0, DstStart=0.0):
    '''
    Given a Dst value at t=0 and an IMF input file, integrate the Burton
    equation over the period spanned by the IMF file and return a time
    vector and Dst.  Uses Runge-Kutta 4 integration.
    '''

    from spacepy.pybats import ImfInput
    from datetime import timedelta

    # Open the IMF file and calculate key values.
    imf = ImfInput(ImfFile)
    Psw, dPsw, Fe = create_functions(imf)

    # Now, use time range to build an array for Dst. 
    TimeStop = (imf['time'][-1] - imf['time'][0]).total_seconds()
    nPoints  = int(TimeStop/dT)
    dst = np.zeros(nPoints+1)
    dst[0] = DstStart

    # Integrate.
    for i in range(nPoints):
        tNow = i*dT
        # Calculate RK4 terms.
        f1 = -aBurt*dst[i] + Psw(tNow) - aBurt*cBurt + Fe(tNow) + dPsw(tNow)
        f2 = -aBurt*(dst[i]+f1*dT/2.0) + Psw(tNow+dT/2.) + \
             -aBurt*cBurt + Fe(tNow+dT/2.0) + dPsw(tNow+dT/2.0)
        f3 = -aBurt*(dst[i]+f2*dT/2.0) + Psw(tNow+dT/2.) + \
             -aBurt*cBurt + Fe(tNow+dT/2.0) + dPsw(tNow+dT/2.0)
        f4 = -aBurt*(dst[i]+f3*dT) + Psw(tNow+dT) + \
             -aBurt*cBurt + Fe(tNow+dT) + dPsw(tNow+dT)
        
        dst[i+1] = dst[i] + dT*(f1+2.*f2+2.*f3+f4)/6.0

    # Create a datetime array corresponding to integration times:
    time = [imf['time'][0] + timedelta(seconds=i*dT) for i in range(nPoints+1)]
    return time, dst

def read_symH(infile):
    '''
    Read a Kyoto WDC Sym-H data file; return a dictionary containing 'time'
    and 'symH'.
    '''

    from dateutil.parser import parse

    # Open file and skip header.
    f = open(infile, 'r')
    line = f.readline()
    while line[0:4] != 'DATE':
        line=f.readline()

    # Slurp rest of file and close.
    lines = f.readlines()
    f.close()

    # Create data container.
    data={}
    data['time'] = np.zeros(len(lines), dtype=object)
    data['symH'] = np.zeros(len(lines))

    # Parse remainder of file.
    for i, l in enumerate(lines):
        parts = l.split()
        data['time'][i] = parse(' '.join(parts[:2]))
        data['symH'][i] = parts[-1]

    return data
        
if __name__ == '__main__':
    
    import matplotlib.pyplot as plt
    from spacepy.pybats import kyoto, apply_smart_timeticks, ImfInput

    infile = 'imf20000715.dat'

    # Obtain actual Dst.
    dst = kyoto.fetch('dst', (2000, 7), (2000, 7))
    symH= read_symH('WWW_aeasy00006705.dat')
    
    # Simple comparison with 5 minute timestep.
    tEul, dEul = burton_euler(infile)
    tRk4, dRk4 = burton_rk4(infile)

    fig= plt.figure(figsize=(8,5.5))
    ax = fig.add_subplot(111)
    ax.plot(dst['time'], dst['dst'], 'k--', symH['time'], symH['symH'], 'k-',
            tEul, dEul, 'b-', tRk4, dRk4, 'r-')
    ax.legend( ['$D_{ST}$', 'Sym-H', 'Burton (Euler)', 
                'Burton (RK4)'], loc='best')
    ax.set_ylabel('Disturbance ($nT$)')
    ax.grid()
    apply_smart_timeticks(ax, tEul, dolabel=True)
    fig.tight_layout()

    # What about convergence?
    fig= plt.figure(figsize=(10,5.5))
    ax = fig.add_subplot(111)
    for dT, style in zip([3600.0, 900.0, 300.0], ['-', '--', ':']):
        tEul, dEul = burton_euler(infile, dT=dT)
        tRk4, dRk4 = burton_rk4(infile, dT=dT)
        ax.plot(tEul, dEul, c='b', ls=style, 
                label='Euler ($\Delta t$={:.0f})'.format(dT))
        ax.plot(tRk4, dRk4, c='r', ls=style, label=
                'RK4 ($\Delta t$={:.0f})'.format(dT))
    
    ax.plot(dst['time'], dst['dst'], 'k--', label=None)
    ax.legend(ncol=3, loc='best')
    ax.set_ylabel('Disturbance ($nT$)')
    ax.grid()
    ax.set_ylim([-850, 20])
    apply_smart_timeticks(ax, tEul, dolabel=True)
    fig.tight_layout()

    # Finally, take one good look at the input parameters.
    imf = ImfInput(infile)
    t=np.array([ (x-imf['time'][0]).total_seconds() for x in imf['time']])
    p, dPdt, F = create_functions(imf)
    
    fig = plt.figure(figsize=(8.5,11))
    
    ax1, ax2, ax3 = [fig.add_subplot(3,1,i+1) for i in range(3)]
    ax1.plot(imf['time'], p(t))
    ax2.plot(imf['time'], dPdt(t))
    ax3.plot(imf['time'], F(t))

    labels = (r'$a*b*P_{SW}$', r'$b*\frac{dP}{dt}$', r'$F(E_Y)$')
    for a, label in zip( [ax1,ax2,ax3], labels ):
        apply_smart_timeticks(a, imf['time'])
        a.set_ylabel(label+' ($nT/s$)', size=14)
        a.grid()
        plt.setp(a, 'xticklabels', [])
        a.get_yticklabels()[0].set_visible(False)
    
    ax1.set_title('Burton Input Values', size=16)
    apply_smart_timeticks(ax3, imf['time'], dolabel=True)
    
    fig.tight_layout()
    fig.subplots_adjust(hspace=0.001)

    
def read_dst(infile):
    import numpy as np
    import datetime as dt


    print '\aTHIS DOES NOT WORK'

    # Check if input is string:
    if type(infile) != type('str'):
        raise TypeError, 'Input file name must be a string.'

    # Open file.
    f = open(infile, 'r')

    # Set start time of file:
    l=f.readline()
    start = dt.datetime(int(l[14:16]+l[3:5]), int(l[5:7]), 1 )

    lines=f.readlines() #we read the datalines at once
    nLines = len(lines)
    time=[]
    dstOut=[] 

    #in this loop we read the string data into numerical format. In each
    #line there are a lot of other data pieces we do not use now
    #we avoid these, and read only the Dst values
    for i in range(len(lines)):
        for k in range(24):
            dstOut.append(int(lines[i][21+4*k:24+4*k])*(-1))
    #create time values for the data set
    for i in range(len(dstOut)):
        time.append(start+dt.timedelta(hours=i))

    time = np.array(time)
        
    return time, dstOut
