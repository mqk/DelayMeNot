import numpy as np
import pandas as pd
from pandas import Series, DataFrame

### Functions to produce delay statistics

def calc_Plate(df, Ntrial=10):
    from copy import copy
    """
        late :: delay >= 30 min
    """

    def Plate(delays):
        N = len(delays)
        Nlate = len(np.where(delays >= 30)[0])
        return (float(Nlate) / N * 100.0)
    
    Plate_struct = {'NumFlights':0,
                    'Plate':0.0,
                    'error':0.0}

    delays = copy(df['ArrDelay'].values)

    Ndelay = len(delays)
    Nhalf = Ndelay / 2

    Plate_struct['NumFlights'] = Ndelay
    Plate_struct['Plate'] = Plate(delays)

    Delta2 = np.zeros(Ntrial)

    for i in xrange(Ntrial):
        np.random.shuffle(delays)

        delays1 = delays[:Nhalf]
        delays2 = delays[Nhalf:]

        Plate1 = Plate(delays1)
        Plate2 = Plate(delays2)

        del delays1, delays2

        Delta2[i] = (Plate1 - Plate2)**2
    
    Plate_struct['error'] = np.sqrt(np.mean(Delta2))

    return Plate_struct


def Plate_binned(flight, df):
    """
    Week, DayOfWeek, DepHour, Carrier
    
    same Week
    same DayOfWeek
    same DepHour

    same Week & DayOfWeek <-- same as DayOfYear?
    same Week & DepHour
    same DayOfWeek & DepHour

    same Week & Carrier
    same DayOfWeek & Carrier
    same DepHour & Carrier

    same Week & DayOfWeek & Carrier
    same Week & DepHour & Carrier
    same DayOfWeek & DepHour & Carrier

    same Week & DayOfWeek & DepHour & Carrier
    """

    Plate = {}

    Plate['All'] = calc_Plate(df)
    
    conditions = [['Week'],
                  ['DayOfWeek'],
                  ['DepHour'],
                  ['Week','DayOfWeek'],
                  ['Week','DepHour'],
                  ['DayOfWeek','DepHour'],
                  ['Week','Carrier'],
                  ['DayOfWeek','Carrier'],
                  ['DepHour','Carrier'],
                  ['Week','DayOfWeek','Carrier'],
                  ['Week','DepHour','Carrier'],
                  ['DayOfWeek','DepHour','Carrier'],
                  ['Week','DayOfWeek','DepHour','Carrier']]

    labels = ['All'] + ['same ' + ' & '.join(x) for x in conditions]
    
    for cond,lab in zip(conditions,labels[1:]):
    	flag = (df['Week'] == df['Week'])  ## all True
        for c in cond:
            flag &= (df[c] == flight[c])
        mdf = df[ flag ]

        Plate[lab] = calc_Plate(mdf)

    ### turn it into a dataframe
    Plate = DataFrame(Plate,columns=labels).T
    
    return Plate



## ======================================================================

def calc_stats(df):
    """
       early :: delay < -15 min
      ontime :: -15 min <= delay < 30 min
        late :: delay >= 30 min
    verylate :: delay >= 60 min

    """

    delays = df['ArrDelay'].values
	
    Nflights = len(df)
    stats_struct = {'NumFlights':Nflights}

    stats_struct['mean_delay'] = delays.mean()
    ## stats_struct['median_delay'] = np.median(delays)
    
    Nearly = len(np.where(delays < -15)[0])
    Pearly = '%.1f%%' % (float(Nearly) / Nflights * 100.0)
    stats_struct['early'] = (Nearly, Pearly)
    
    Nontime = len(np.where( (delays >= -15) & (delays < 30) )[0])
    Pontime = '%.1f%%' % (float(Nontime) / Nflights * 100.0)
    stats_struct['ontime'] = (Nontime, Pontime)

    Nlate = len(np.where(delays >= 30)[0])
    Plate = '%.1f%%' % (float(Nlate) / Nflights * 100.0)
    stats_struct['late'] = (Nlate, Plate)

    Nverylate = len(np.where(delays >= 60)[0])
    Pverylate = '%.1f%%' % (float(Nverylate) / Nflights * 100.0)
    stats_struct['verylate'] = (Nverylate, Pverylate)

    return stats_struct


def delay_statistics(flight, df):
    """
    Week, DayOfWeek, DepHour, Carrier
    
    same Week
    same DayOfWeek
    same DepHour

    same Week & DayOfWeek <-- same as DayOfYear?
    same Week & DepHour
    same DayOfWeek & DepHour

    same Week & Carrier
    same DayOfWeek & Carrier
    same DepHour & Carrier

    same Week & DayOfWeek & Carrier
    same Week & DepHour & Carrier
    same DayOfWeek & DepHour & Carrier

    same Week & DayOfWeek & DepHour & Carrier
    """

    delay_stats = {}

    conditions = [['Week'],
                  ['DayOfWeek'],
                  ['DepHour'],
                  ['Week','DayOfWeek'],
                  ['Week','DepHour'],
                  ['DayOfWeek','DepHour'],
                  ['Week','Carrier'],
                  ['DayOfWeek','Carrier'],
                  ['DepHour','Carrier'],
                  ['Week','DayOfWeek','Carrier'],
                  ['Week','DepHour','Carrier'],
                  ['DayOfWeek','DepHour','Carrier'],
                  ['Week','DayOfWeek','DepHour','Carrier']]

    labels = ['same ' + ' & '.join(x) for x in conditions]
	
    for cond,lab in zip(conditions,labels):
    	flag = (df['Week'] == df['Week'])  ## all True
        for c in cond:
            flag &= (df[c] == flight[c])
        mdf = df[ flag ]

        delay_stats[lab] = calc_stats(mdf)

        
    ### turn it into a dataframe
    delay_stats = DataFrame(delay_stats,columns=labels,index=[['NumFlights', 'mean_delay', 'early', 'ontime', 'late', 'verylate']]).T
    
    return delay_stats


