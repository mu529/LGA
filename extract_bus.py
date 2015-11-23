# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 13:50:52 2015

Outbound
    First stop: MTA_403117
    125th and St. Nicholas: MTA_402656
    2nd Ave, before bridge: MTA_403673
    Astoria Blvd NQ: MTA_503357
    LGA Term D: MTA_904199

Return 
    30th and Hoyt: MTA_504007
    2nd Ave, off bridge: MTA_403676
    125th and Malcom X: MTA_402507
    Barnard 119th: MTA_503357

M60 id = 'MTA NYCT_M60+'
30th Ave stop = 'MTA_503357'
M60 stops = 'data/gtfs-bus/m60_stops.csv'

Q70 id: 'MTABC_Q70'
Roosevelt stop: 'MTA_553285'
Q70 stops: 'data/gtfs-mtabc/q70_stops.csv'

@author: murbanek
"""

# NOTE: need to run earliness_distribution to get dowarray and dowdict before running this
busline = 'MTA NYCT_M60+'
modeled_stop = 'MTA_503357'
stopfile = 'data/gtfs-bus/m60_stops.csv'
expected_ride = 20

import pandas as pd
import numpy as np
import os
from datetime import timedelta
import pylab as pl
import pickle

import warnings
warnings.simplefilter(action = "ignore", category = RuntimeWarning)

stopseq = pd.read_csv(stopfile)
stopseq['next_scheduled_stop_id'] = 'MTA_' + stopseq['stop_id'].astype(str)
del stopseq['stop_id']
stopseq = stopseq.set_index('next_scheduled_stop_id')

os.chdir('data/bustime/')
busline_data = pd.DataFrame()
# stop_data_max = pd.DataFrame()
# stop_data_min = pd.DataFrame()
for f in os.listdir():
    busimport = pd.read_csv(f, sep='\t')
    busimport = busimport[busimport['inferred_route_id']==busline]
    busimport = busimport.join(stopseq, on='next_scheduled_stop_id', how='left', rsuffix='_r')
    # stopimport = busimport[busimport['next_scheduled_stop_id']==stopid]
    busline_data = busline_data.append(busimport)
    # stop_data_max = stop_data_max.append(stopimport.groupby(['inferred_trip_id','vehicle_id']).max())
    # stop_data_min = stop_data_min.append(stopimport.groupby(['inferred_trip_id','vehicle_id']).min())

del busimport
os.chdir('..')
os.chdir('..')
print('Done with bustime data import')

busline_data.sort(columns=['vehicle_id','time_received'], inplace=True)
busline_data.reset_index(inplace=True)

stoparrays = {}
for stopid in stopseq.index[1:-1]:
    
# set each row as prior-approaching-after based on boolean results

    busline_data['relative_position'] = ''
    busline_data.loc[busline_data['stop_sequence'] < stopseq.loc[stopid][0], 'relative_position'] = 'prior'
    busline_data.loc[busline_data['stop_sequence'] == stopseq.loc[stopid][0], 'relative_position'] = 'approaching'
    busline_data.loc[busline_data['stop_sequence'] > stopseq.loc[stopid][0], 'relative_position'] = 'passed'
    
    busline_data['stop_ind'] = 0
    
    for i in busline_data.index[:-2]:
        if busline_data.loc[i]['relative_position'] == busline_data.loc[i+1]['relative_position']:
            continue
        elif (busline_data.loc[i]['relative_position'] == 'approaching' and busline_data.loc[i+1]['relative_position'] == 'passed'):
            busline_data.loc[i,'stop_ind'] = 1
        elif (busline_data.loc[i]['relative_position'] == 'approaching' and busline_data.loc[i+2]['relative_position'] == 'passed'):
            busline_data.loc[i,'stop_ind'] = 1
        else:
            continue
    
    stop_data = busline_data[busline_data['stop_ind']==1].sort(columns=['time_received'])
    stop_data.reset_index(inplace=True)
    stop_data['arrival_target'] = pd.to_datetime(stop_data['time_received']) + timedelta(minutes=expected_ride)
    # referencetimestamp = int(time.mktime(time.strptime(stop_data.time_received.min(), '%Y-%m-%d %H:%M:%S'))) - time.timezone
    stop_data['DOW'] = stop_data['arrival_target'].apply(lambda x : x.dayofweek).astype(int)
    stop_data['timestep'] = stop_data['arrival_target'].apply(lambda x : (12*x.hour + x.minute/5)).astype(int)
    
    
    stop_data['headway'] = np.nan
    stop_data['headway'][1:] = (pd.to_datetime(stop_data['time_received']).diff()[1:]/np.timedelta64(1,'m')).astype(int)
    # add loop to determine bunching (1 for first bus, 2 for 2nd bus)
    stop_data['spacing_ind']=0
    stop_data.loc[stop_data['headway']>15,'spacing_ind'] = 1
    stop_data.loc[stop_data['headway']<=3,'spacing_ind'] = 2
    
    stoparrays[stopid] = stop_data
    print('Done with analysis of stop ' + stopid)

stopstats = pd.DataFrame(columns=['obs','dist_mean','dist_std','hw_mean','hw_std','pct_longhw','pct_shorthw'])
for stopid in stoparrays.keys():
    stopstats.loc[stopseq.loc[stopid]['stop_sequence'],'obs'] = stoparrays[stopid].shape[0]
    stopstats.loc[stopseq.loc[stopid]['stop_sequence'],'dist_mean'] = stoparrays[stopid]['distance_along_trip'].mean()
    stopstats.loc[stopseq.loc[stopid]['stop_sequence'],'dist_std'] = stoparrays[stopid]['distance_along_trip'].std()
    stopstats.loc[stopseq.loc[stopid]['stop_sequence'],'hw_mean'] = stoparrays[stopid]['headway'].mean()
    stopstats.loc[stopseq.loc[stopid]['stop_sequence'],'hw_std'] = stoparrays[stopid]['headway'].std()
    stopstats.loc[stopseq.loc[stopid]['stop_sequence'],'pct_longhw'] = stoparrays[stopid].groupby('spacing_ind').size()[1]/stop_data.shape[0]
    stopstats.loc[stopseq.loc[stopid]['stop_sequence'],'pct_shorthw'] = stoparrays[stopid].groupby('spacing_ind').size()[2]/stop_data.shape[0]

stopstats.to_csv(busline + '_stats.csv')
with open(busline + '_stoparrays.pkl', 'wb') as output:
    pickle.dump(stoparrays, output, pickle.HIGHEST_PROTOCOL)
    
##### end of busline analysis
