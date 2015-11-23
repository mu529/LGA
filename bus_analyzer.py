# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 12:21:56 2015

@author: murbanek
"""
busline = 'MTA NYCT_M60+'
modeled_stop = 'MTA_503357'
comparison_stop = 'MTA_403122'
stopfile = 'data/gtfs-bus/m60_stops.csv'
expected_ride = 20

import pandas as pd
import numpy as np
import os
from datetime import timedelta
import pylab as pl
import pickle
from scipy import stats

import warnings
warnings.simplefilter(action = "ignore", category = RuntimeWarning)

stopstats = pd.read_csv(busline + '_stats.csv')
with open(busline + '_stoparrays.pkl', 'rb') as input:
    stoparrays = pickle.load(input)

##### begin individual stop analysis
stop_data = stoparrays[modeled_stop]

for i in stop_data.index:
    if i == 0:
        print(dowarray[stop_data.loc[i,'DOW']-1,stop_data.loc[i,'timestep']])
    else:
        stop_data.loc[i,'demand'] = dowarray[dowdict[stop_data.loc[i,'DOW']]][stop_data.loc[i-1,'timestep']+1:stop_data.loc[i,'timestep']+1].sum()

demands1 = stop_data['demand'].dropna().values
headways1 = stop_data['headway'].dropna().values


# stop_data.to_csv(stopid + '_with_demand.csv')
"""
extra code for diagnosing one single vehicle on one single day

busimport = pd.read_csv('data/bustime/MTA-Bus-Time_.2014-08-10.txt', sep='\t')
busimport[busimport['vehicle_id']==5972].to_csv('5972_dump_10aug.csv')
busimport[busimport['vehicle_id']==5983].to_csv('5983_dump_10aug.csv')
busimport[busimport['vehicle_id']==5974].to_csv('5974_dump_10aug.csv')
"""


## for each tripid, get me the max time stamp
# stopimport.groupby('inferred_trip_id').max().to_csv('max_dump.csv')

# stop_data_max.to_csv(stopid + '_data_max.csv')
# stop_data_min.to_csv(stopid + '_data_min.csv')

figure, ax = pl.subplots(figsize=(10,10))
ax.set_xlabel('Trip Headway (Minutes)',fontsize=20)
ax.set_ylabel('Frequency, n=7,832',fontsize=20)
ax.set_title('Fig. 4: Headway Between Bus Arrivals \n M60 SBS at stop ' + modeled_stop,fontsize=24)
ax.hist([stop_data['headway'].dropna()], bins=20, range=[0,60], color='g')

figure, ax = pl.subplots(figsize=(10,10))
ax.set_xlabel('Nominal demand on bus trip',fontsize=20)
ax.set_ylabel('Frequency, n=7,832',fontsize=20)
ax.set_title('Fig. 5: Distribution of Simulated Demand \nFor Each Vehicle - M60 SBS',fontsize=24)
ax.hist(demands1, bins=20, range=[0,2000])

a = stop_data[stop_data['spacing_ind']==0]['demand'].dropna()
b = stop_data[stop_data['spacing_ind']==1]['demand'].dropna()
c = stop_data[stop_data['spacing_ind']==2]['demand'].dropna()

figure, ax = pl.subplots(figsize=(10,10))
ax.set_xlabel('Nominal demand on bus trip',fontsize=20)
ax.set_ylabel('Frequency, n=7,832',fontsize=20)
ax.set_title('Fig. 7: Distribution of Simulated Demand\n with Headway Categories - M60 SBS',fontsize=24)
ax.hist([a,b,c], bins=20, range=[0,2000], stacked=True)
ax.legend((a,b,c), labels=('Normal Headway','>15 Minute Headway','<=3 Minute Headway'), fontsize=18, loc='upper right')


# KS test to compare headway distributions
stop_data = stoparrays[comparison_stop]

for i in stop_data.index:
    if i == 0:
        print(dowarray[stop_data.loc[i,'DOW']-1,stop_data.loc[i,'timestep']])
    else:
        stop_data.loc[i,'demand'] = dowarray[dowdict[stop_data.loc[i,'DOW']]][stop_data.loc[i-1,'timestep']+1:stop_data.loc[i,'timestep']+1].sum()

demands2 = stop_data['demand'].dropna().values
headways2 = stop_data['headway'].dropna().values

print('Headway moments at stop '+ modeled_stop + ':')
print(headways1.mean())
print(headways1.std())
print('Demand mean at stop '+ modeled_stop + ':')
print(demands1.mean())
print('Demand standard deviation at stop '+ modeled_stop + ':')
print(demands1.std())
print('KS Statistic and p-value:')
print(stats.ks_2samp(headways1,headways2))