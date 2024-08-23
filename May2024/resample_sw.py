#!/usr/bin/env python
'''
This script uses pandas to resample an IMF file and 
a solar wind file and save them together as a CDF 
for propagation later.
'''

import sys
from glob import glob
from argparse import ArgumentParser, RawDescriptionHelpFormatter

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.constants import k, m_p
from datetime import datetime, timedelta

from spacepy import pycdf

parser = ArgumentParser(description=__doc__,
                        formatter_class=RawDescriptionHelpFormatter)

parser.add_argument('-b', '--start', default=None, help="Set the start date and " +
                    "time of the simulation using the format " +
                    "YYYY-MM-DDTHH:MN:SS.")
parser.add_argument('-e', '--end', default=None, help="Set the start date and " +
                    "time of the simulation using the format " +
                    "YYYY-MM-DDTHH:MN:SS.")
parser.add_argument('-m', '--mfi', help='path to MFI file.')
parser.add_argument('-s', '--swe', help='path to SWE file.')

# Handle arguments:
args = parser.parse_args()

# Find files:
swefile = glob(args.swe)[0]
mfifile = glob(args.mfi)[0]

# Read in data:
swe = pycdf.CDF(swefile)
swe.readonly(False)
mfi = pycdf.CDF(mfifile)

# Get satellite name:
if swefile[0:2] == 'ac':
    sat = 'ace'
elif swefile[0:2] == 'wi':
    sat = 'wind'
else:
    print('Unknown data source. Please develop the code to handle this!')
    sys.exit()

def resample_df(df):
    '''Resamples a pandas df to one minute resolution.'''
    df = df.resample('30s').mean()
    df = df.interpolate(method='linear')
    df = df.resample('60s').mean()

    return df

# Create dataframes:
if sat == 'ace':
    swedf = pd.DataFrame(np.vstack((swe['Np'],swe['Tpr'], swe['VX_GSM'],
                                    swe['VY_GSM'], swe['VZ_GSM'],
                                    swe['alpha_ratio'])).transpose(),
                          index=swe['Epoch'], columns=['Np','TEMP', 'VX',
                                                       'VY', 'VZ', 'alpha_ratio'])
    #swedf = swedf[~swedf.index.duplicated(keep='first')]
    swevars = ['Np','TEMP', 'VX', 'VY', 'VZ', 'alpha_ratio'] 

    mfidf = pd.DataFrame(np.vstack((mfi['BGSM'][:,0], mfi['BGSM'][:,1], mfi['BGSM'][:,2],
                                    mfi['SC_pos_GSM'][:,0], mfi['SC_pos_GSM'][:,1],
                                    mfi['SC_pos_GSM'][:,2])).transpose(),
                         index=mfi['Epoch'], columns=['BX', 'BY', 'BZ',
                                                      'XGSM', 'YGSM', 'ZGSM'])

    # Convert ACE position from km to RE:
    for c in 'XYZ':
        mfidf[c+'GSM'] = mfidf[c+'GSM']/6371.
else:
    # Convert thermal speed to temperature in Kelvin:
    swe['TEMP'] = (m_p/(2*k))*(swe['Proton_W_moment'][...]*1000)**2

    # wi_h1_swe velocity vars will be in GSE. Convert to GSM:
    import utils
    swe['VX_GSM'], swe['VY_GSM'], swe['VZ_GSM'] = \
        utils.convertCoords(swe['Proton_VX_moment'][...],
                            swe['Proton_VY_moment'][...],
                            swe['Proton_VZ_moment'][...], 'GSE', 'GSM',
                            swe['Epoch'][...])
    
    swedf = pd.DataFrame(np.vstack((swe['Proton_Np_moment'],swe['TEMP'], swe['VX_GSM'],
                                    swe['VY_GSM'], swe['VZ_GSM'])).transpose(),
                          index=swe['Epoch'], columns=['Np','TEMP', 'VX',
                                                       'VY', 'VZ'])
    #swedf = swedf[~swedf.index.duplicated(keep='first')]
    swevars = ['Np','TEMP', 'VX', 'VY', 'VZ']

    mfidf = pd.DataFrame(np.vstack((mfi['BGSM'][:,0], mfi['BGSM'][:,1], mfi['BGSM'][:,2],
                                    mfi['PGSM'][:,0], mfi['PGSM'][:,1],
                                    mfi['PGSM'][:,2])).transpose(),
                         index=mfi['Epoch'], columns=['BX', 'BY', 'BZ',
                                                      'XGSM', 'YGSM', 'ZGSM'])
print(mfidf)
print(swedf)

# Replace bad values with NaNs:
mfidf[mfidf < -10000.] = np.nan
swedf[swedf < -10000.] = np.nan

# HARD-CODING FOR GANNON STORM
for k in swedf:
    if k != 'TEMP':
        swedf[k][swedf[k] > 50000.] = np.nan
swedf['TEMP'][swedf['TEMP'] > 10000000.] = np.nan

# Resample data to one minute:
swedf = resample_df(swedf)
mfidf = resample_df(mfidf)

# If necessary, cut swe data to desired time limit:
if args.start:
    start = datetime.strptime(args.start, '%Y-%m-%dT%H:%M:%S')
    swedf = swedf.drop(swedf.loc[(swedf.index < start)].index)
if args.end:
    end = datetime.strptime(args.end, '%Y-%m-%dT%H:%M:%S')
    swedf = swedf.drop(swedf.loc[(swedf.index >= end)].index)

print(mfidf)
print(swedf)

# Test plot:
#swedf.plot(subplots=True)
#plt.show()
#mfidf.plot(subplots=True)
#plt.show()

# Combine MFI and SWE data into a single CDF and save:
first_time = datetime.strftime(mfi['Epoch'][0], '%Y%m%d_%H%M%S')
data = pycdf.CDF(f'{sat}_{first_time}_merged.cdf', '')

dts = swedf.index.to_pydatetime()
data['Epoch'] = dts

for var in swevars:
    data[var] = swedf[var]
for var in ['BX', 'BY', 'BZ','XGSM', 'YGSM', 'ZGSM']:
    data[var] = mfidf[var]

print(data)
data.close()
                               
