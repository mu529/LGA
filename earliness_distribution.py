# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 00:51:39 2015

@author: murbanek
"""

import pandas as pd
import numpy as np
import pylab as pl

np.random.seed(420)

flights = pd.read_csv('data/LGA_departures_sample.csv')
# convert time string to datetime in local
flights['departuredatetime'] = pd.to_datetime((flights.departuretime - 5*60*60), unit='s')
flights['total_seats'] = flights.seats_cabin_first + flights.seats_cabin_business + flights.seats_cabin_coach 

# calculate relative timesteps starting three hours prior to earliest flight
# still in epoch time (seconds)

referencedate = flights['departuredatetime'].min().value//10**9 - flights['departuredatetime'].min().hour*60*60 - flights['departuredatetime'].min().minute*60 + 5*60*60
# referencetimestamp = flights.departuretime.min() - 3*60*60
flights['depttimestep'] = np.ceil((flights['departuretime']-referencedate)/(5*60)).astype(int)

# categorize departures based on local departure time
flights.loc[flights['departuredatetime'].apply(lambda x: x.hour) <= 7,'timeofday'] = 'EarlyAM'
flights.loc[flights['departuredatetime'].apply(lambda x: x.hour) >= 17,'timeofday'] = 'Evening'

# instead of time array starting at beginning, it should start at mightnight the first day and be exactly 7 days long
# timearray = np.zeros((len(flights),288*(np.ceil(flights.depttimestep.max()/288).astype(int))),dtype=np.int)

timearray = np.zeros((len(flights),288*7),dtype=np.int)
# need to break into weekday, too

for i in flights.index:
    if flights.loc[i,'timeofday'] == 'EarlyAM':
        arrivals = 20 + 5*np.random.chisquare(10, size=flights.loc[i,'total_seats'])
        bins = np.histogram(arrivals, bins=36, range=(0,180))[0]
    elif flights.loc[i, 'timeofday'] == 'Evening':
        arrivals = 20 + 5*np.random.chisquare(14, size=flights.loc[i,'total_seats'])
        bins = np.histogram(arrivals, bins=36, range=(0,180))[0]
    else:
        arrivals = 20 + 5*np.random.chisquare(12, size=flights.loc[i,'total_seats'])
        bins = np.histogram(arrivals, bins=36, range=(0,180))[0]
    # flights.loc[i,'departuretime'] - referencedate is the span of seconds up till departuretime
# WTF
#    firsttimestep = (flights.loc[i,'departuretime'] - referencedate)//(60*5) - (12*5)
#    timearray[i,flights.loc[i,'depttimestep']-36:flights.loc[i,'depttimestep']] = bins[::-1]
    timearray[i,flights.loc[i,'depttimestep']-36:flights.loc[i,'depttimestep']] = bins[::-1]

# print(timearray.sum())
# halfhourarray = timearray.reshape(timearray.shape[0],np.divide(timearray.shape[1],5).astype(int),5)
dowarray = timearray.reshape(timearray.shape[0],np.divide(timearray.shape[1],288).astype(int),288).sum(axis=0)
dowdict = {pd.to_datetime(referencedate,unit='s').dayofweek : 0,
           pd.to_datetime(referencedate+1*24*60*60,unit='s').dayofweek : 1,
           pd.to_datetime(referencedate+2*24*60*60,unit='s').dayofweek : 2,
           pd.to_datetime(referencedate+3*24*60*60,unit='s').dayofweek : 3,
           pd.to_datetime(referencedate+4*24*60*60,unit='s').dayofweek : 4,
           pd.to_datetime(referencedate+5*24*60*60,unit='s').dayofweek : 5,
           pd.to_datetime(referencedate+6*24*60*60,unit='s').dayofweek : 6}

"""
figure, ax = pl.subplots(figsize=(10,10))
x = np.arange(halfhourarray.shape[1])
y = halfhourarray.sum(axis=2).sum(axis=0)
ax.plot(x, y)
"""
# Line of 5 minute time steps for each day of week

figure, ax = pl.subplots(figsize=(10,10))
x = np.arange(dowarray.shape[1])
ax.set_xlabel('5-Minute Time Step (00:00-23:55)',fontsize=20)
ax.set_ylabel('Passengers Arriving',fontsize=20)
ax.set_title('Fig. 3: Aggregated Distribution of Passenger Earliness\n by Day of Week at LGA Airport',fontsize=24)
for dow in np.arange(dowarray.shape[0]):
    ax.plot(x, dowarray[dow]+1)
