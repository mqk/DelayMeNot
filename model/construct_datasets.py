import numpy as np
import time, datetime, sys
import pandas as pd
from pandas import DataFrame

def construct_datasets(Origin, min_year=2008, subsample=None):
    import MySQLdb

    ## print '   Connecting to database...'
    ## time0 = time.time()
    db = MySQLdb.connect(host="localhost",
                         user="mqk",
                         passwd="z2yv52K*hJ<otclN",
                         db="DelayMeNot",
                         local_infile = 1)
    ## print '       That took %.1f seconds' % (time.time() - time0)

    cur = db.cursor()

    ### flights origination from Origin
    print '   Querying database...'
    time0 = time.time()
    ## if min_year == 2008:        
    ##     cur.execute("SELECT Year, Month, DayofMonth, DayOfWeek, CRSDepTime, CRSArrTime, UniqueCarrier, CRSElapsedTime, ArrDelay, Dest, Distance FROM flights_2008_2013 WHERE Origin = '%s';" % (Origin))
    ## else:
    ##     cur.execute("SELECT Year, Month, DayofMonth, DayOfWeek, CRSDepTime, CRSArrTime, UniqueCarrier, CRSElapsedTime, ArrDelay, Dest, Distance FROM flights WHERE Origin = '%s' AND Year >= %d;" % (Origin, min_year))        

    ## print "SELECT Year, Month, DayofMonth, DayOfWeek, CRSDepTime, CRSArrTime, UniqueCarrier, CRSElapsedTime, ArrDelay, Dest, Distance FROM flights WHERE Origin = '%s' AND Year >= %d;" % (Origin, min_year) 
    cur.execute("SELECT Year, Month, DayofMonth, DayOfWeek, CRSDepTime, CRSArrTime, UniqueCarrier, CRSElapsedTime, ArrDelay, Dest, Distance FROM flights WHERE Origin = '%s' AND Year >= %d;" % (Origin, min_year))        

    print '      That took %.1f seconds.' % (time.time() - time0)

    rows = cur.fetchall()

    
    ### Convert to DataFrame
    print '   Converting to DataFrame...'
    time0 = time.time()

    df = DataFrame(list(rows), columns=['Year', 'Month', 'DayOfMonth', 'DayOfWeek', 'ScheduledDepartureTime', 'ScheduledArrivalTime', 'Carrier', 'ScheduledElapsedTime', 'ArrivalDelay', 'Destination', 'Distance'])
    del rows
    
    ### drop columns without delays (cancellations)
    df = df.dropna()

    ### Create some auxiliary columns

    df['DayOfYear'] = df.apply( lambda x: datetime.datetime(x['Year'],x['Month'],x['DayOfMonth']).timetuple().tm_yday, axis=1)
    df['Week'] = df['DayOfYear'] / 7 + 1
    df['ScheduledDepartureHour'] = df['ScheduledDepartureTime']/100 + df['ScheduledDepartureTime']%100 / 60.0
    df['ScheduledArrivalHour'] = df['ScheduledArrivalTime']/100 + df['ScheduledArrivalTime']%100 / 60.0

    df = df.drop(['ScheduledDepartureTime','ScheduledArrivalTime'],axis=1)

    ### Add DaysFromNearestHoliday column
    df = distance_to_holiday(df)
    
    ## df.head()
    print '      That took %.1f seconds.' % (time.time() - time0)


    ### subsample by a factor of 10
    if subsample is not None:
        print '   Subsampling (x%d) DataFrame...' % subsample
        time0 = time.time()
        df = df.ix[::subsample]
        print '   That took %.1f seconds.' % (time.time() - time0)
    ## print len(df)

    ## ### Normalize columns  (*** this isn't necessary for RandomForest ***)
    ## def normalize(var):
    ##     return (var - var.min()).astype(float) / (var.max() - var.min())
    ## df['Year'] = normalize(df['Year'])
    ## df['Month'] = normalize(df['Month'])
    ## df['DayOfMonth'] = normalize(df['DayOfMonth'])
    ## df['DayOfWeek'] = normalize(df['DayOfWeek'])
    ## df['DayOfYear'] = normalize(df['DayOfYear'])
    ## df['Week'] = normalize(df['Week'])
    ## df['ScheduledDepartureHour'] = normalize(df['ScheduledDepartureHour'])
    ## df['ScheduledArrivalHour'] = normalize(df['ScheduledArrivalHour'])
    ## df['ScheduledElapsedTime'] = normalize(df['ScheduledElapsedTime'])
    ## df['Distance'] = normalize(df['Distance'])
    ## df['DaysFromNearestHoliday'] = normalize(df['DaysFromNearestHoliday'])

    ## print df.head()


    ##### Dummification should happen after unpickling, since including all the dummified columns makes the pickles huge!
        
    ## ### "Dummify" the categorical 'Carrier' and 'Destination' columns,
    ## ### and add the dummies to the table, but drop the first dummy
    ## ### column to avoid "dummy variable trap".

    ## dummies = pd.get_dummies(df['Carrier'],prefix='Carrier')
    ## ## ## print dummies.columns
    ## df = df.join(dummies.ix[:,1:])

    ## dummies = pd.get_dummies(df['Destination'],prefix='Destination')
    ## df = df.join(dummies.ix[:,1:])

    ## ### Drop dummified columns
    ## df = df.drop(['Carrier','Destination'],axis=1)
    
    ## print len(df.columns)
    ## print df.head()


    ### Shuffle and create separate train and test datasets
    print '   Separating into training and testing dataset...'
    time0 = time.time()
    df = df.reindex(np.random.permutation(df.index))
    Nrow = len(df)
    Ntrain = int(2.0/3.0*Nrow)
    Ntest = Nrow - Ntrain
    data_train = df[:Ntrain]
    data_test = df[Ntrain:]
    del df
    print '       That took %.1f seconds.' % (time.time() - time0)

    ### Close up the cursor and database
    cur.close()
    db.close()    
        
    return (data_train, data_test)


def save_to_pickle(data_train, data_test, filename='test_dataset.pkl', gzip=True):
    import cPickle
    import subprocess
    
    f = open(filename,'wb')
    cPickle.dump((data_train, data_test),f,2)
    f.close()

    if gzip:
        subprocess.call('gzip %s' % filename, shell=True)
    
def load_from_pickle(filename='test_dataset.pkl', gzip=True):
    import cPickle
    import subprocess

    if gzip:
        subprocess.call(['gunzip','%s.gz' % filename])
    
    f = open(filename,'rb')
    (data_train, data_test) = cPickle.load(f)
    f.close()

    if gzip:
        subprocess.call(['gzip', filename])
    
    return (data_train, data_test)

def distance_to_holiday(df):
    import MySQLdb
    db = MySQLdb.connect(host="localhost",
                         user="mqk",
                         passwd="z2yv52K*hJ<otclN",
                         db="DelayMeNot",
                         local_infile = 1)

    cur = db.cursor()
    cur.execute("SELECT Month, Day, Year from holidays;")
    rows = cur.fetchall()

    hdf = DataFrame(list(rows), columns=['Month', 'Day', 'Year'])
    del rows

    holiday_dates = hdf.apply(lambda x: datetime.date(x['Year'],x['Month'],x['Day']),axis=1).values

    df['DaysFromNearestHoliday'] = df.apply(lambda x: abs(holiday_dates - datetime.date(x['Year'],x['Month'],x['DayOfMonth'])).min().days, axis=1)

    cur.close()
    db.close()    
    
    return df


def batch_by_Origin():
    import cPickle
    f = open('Origin_list.pkl','rb')
    origin_dict = cPickle.load(f)
    f.close()

    origins = origin_dict.keys()
    origins = [x for (y,x) in sorted(zip(origin_dict.values(),origins),reverse=True)]

    for origin in origins:
        if origin_dict[origin] < 50000: continue

        if origin in ['ORD','ATL','DFW']: continue

        print 'Fetching data for flights originating from %s (Nflights=%d)...' % (origin, origin_dict[origin])        
        (data_train, data_test) = construct_datasets(origin)

        pickle_filename = '/data/DelayMeNot/data/pickles_by_origin/datasets_%s.pkl' % origin
        print 'Pickling to %s...' % pickle_filename
        time0 = time.time()
        save_to_pickle_gzip(data_train, data_test, filename=pickle_filename)
        dt = time.time() - time0
        print '   That took %.1f seconds.' % dt
        print
        
