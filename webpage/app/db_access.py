import MySQLdb

import pandas as pd
from pandas import Series, DataFrame
import datetime
import numpy as np

### Functions to produce delay statistics

def calc_stats(df):
    """
       early :: delay < -15 min
      ontime :: -15 min <= delay < 30 min
        late :: delay >= 30 min
    verylate :: delay >= 60 min

    """

    delays = df['ArrDelay'].values
	
    Nflights = len(df)
    if Nflights == 0:
        return False
    
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

    import make_plots as mp
    
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
    plotlabels = [''.join(x) for x in conditions]
    
    for cond,lab,plab in zip(conditions,labels,plotlabels):
        flag = (df['Week'] == df['Week'])  ## all True
        for c in cond:
            flag &= (df[c] == flight[c])
        mdf = df[ flag ]
        this_stats = calc_stats(mdf)
        if this_stats:
            delay_stats[lab] = this_stats

        ## mp.delay_histogram(mdf['ArrDelay'],pid=plab)
    
    ### turn it into a dataframe
    delay_stats = DataFrame(delay_stats,columns=labels,index=[['NumFlights', 'mean_delay', 'early', 'ontime', 'late', 'verylate']]).T
    delay_stats.index.name = 'Grouping'

    return delay_stats



def connect():
    """
    Connect to database.
    Returns database and cursor handles.
    """
    db = MySQLdb.connect(host="virginia.dyndns-at-home.com",
                        user="mqk",
                        passwd="z2yv52K*hJ<otclN",
                        db="DelayMeNot")
    cur = db.cursor()

    return db, cur


def close_up(db,cur):
    """
    Close cursor and database.
    """
    cur.close()
    db.close()
    
    return True


def get_flights_from_route(cur, origin, destination):
    """
    Returns a dataframe for all flights matching origin, destination.
    """

    import time
    
    ### MySQL query
    time0 = time.time()
    cur.execute("SELECT Year, Month, DayofMonth, DayOfWeek, CRSDepTime, UniqueCarrier, ArrDelay FROM flights_100000 WHERE Origin = %s and Dest = %s;", (origin, destination))
    rows = cur.fetchall()
    td = time.time() - time0
    print 'Database query took %.2f seconds.' % td
    
    ### Convert to dataframe
    df = DataFrame(list(rows), columns=['Year', 'Month', 'DayOfMonth', 'DayOfWeek', 'CRSDepTime', 'Carrier', 'ArrDelay'])

    ### Drop columns without delays (cancellations)
    df = df.dropna()
    
    ### Create some auxiliary columns
    df['DayOfYear'] = df.apply( lambda x: datetime.datetime(x['Year'],x['Month'],x['DayOfMonth']).timetuple().tm_yday, axis=1)
    df['Week'] = df['DayOfYear'] / 7 + 1
    df['DepHour'] = df['CRSDepTime']/100

    ### Drop unused columns
    df = df.drop(['DayOfMonth','CRSDepTime'],axis=1).sort_index(axis=1)

    ## df.head()
    
    return df


