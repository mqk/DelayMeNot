import cPickle
import time
import datetime
import numpy as np
import pandas as pd
from pandas import DataFrame

def apply_RF_model(flights):
    """
    flights is a DataFrame.
    """

    hdf = pd.read_fwf('data/US_holidays_1997-2020.txt',colspecs=[[0,2],[3,5],[6,10],[12,50]],header=None,names=['Month','Day','Year','Holiday'])
    hdf['Holiday'] = hdf['Holiday'].apply(lambda x: x[:-1])
    holiday_dates = hdf.apply(lambda x: datetime.date(x['Year'],x['Month'],x['Day']),axis=1).values
    del hdf

    ## origins = list(np.unique(np.array([x['Origin'] for x in flights])))
    origins = flights['Origin'].unique()
    
    ## for orig in origins:
    for orig in ['SFO']:
        print 'Unpickling RandomForest model...'
        time0 = time.time()       
        f = open('RandomForest_models/rfm_%s.pkl' % orig, 'rb')
        (rfor,model_summary) = cPickle.load(f)
        f.close()
        print '   That took %.1f seconds.' % (time.time() - time0)

        ## set to single core for model evaluation
        rfor.n_jobs = 1
        
        train_cols = model_summary['training_columns']
        
        df = flights[ flights['Origin'] == orig ]
        df['Year'] = df['DepartureDateTime'].apply(lambda x: x.year)
        df['Month'] = df['DepartureDateTime'].apply(lambda x: x.month)
        df['DayOfMonth'] = df['DepartureDateTime'].apply(lambda x: x.day)
        df['DayOfWeek'] = df['DepartureDateTime'].apply(lambda x: x.weekday()+1)
        df['DayOfYear'] = df['DepartureDateTime'].apply(lambda x: x.timetuple().tm_yday)
        df['Week'] = df['DayOfYear'] / 7 + 1
        df['ScheduledDepartureHour'] = df['DepartureDateTime'].apply(lambda x: x.hour)
        df['ScheduledArrivalHour'] = df['ArrivalDateTime'].apply(lambda x: x.hour)
        df['DaysFromNearestHoliday'] = df['DepartureDateTime'].apply(lambda x: abs(holiday_dates - x.date()).min().days)

        FlightID = df['FlightID'].values
        
        df = df.drop(['ArrivalDate','ArrivalDateAdjustment','ArrivalDateTime','ArrivalTime','Carrier','DepartureDate','DepartureDateAdjustment','DepartureDateTime','DepartureTime','FlightID','FlightNumber','Origin'],axis=1)
                
        df.rename(columns={'FlightDuration':'ScheduledElapsedTime',
                           'CarrierCode':'Carrier'}, inplace=True)


        dummies = pd.get_dummies(df['Carrier'],prefix='Carrier')
        df = df.join(dummies.ix[:,1:])

        dummies = pd.get_dummies(df['Destination'],prefix='Destination')
        df = df.join(dummies.ix[:,1:])
        

        ### Add zero columns for any missing columns
        for tc in train_cols:
            if tc not in df.columns:
                df[tc] = np.zeros_like(df['Year'],dtype=float)

        ### Drop any columns that are not in train_cols
        cols_to_drop = []
        for c in df.columns:
            if c not in train_cols:
                cols_to_drop.append(c)
        df = df.drop(cols_to_drop,axis=1)


        ### re-order the columns
        df = df.ix[:, train_cols]                


        ### at last, apply the model
        Pdelay = dict( zip(FlightID, rfor.predict_proba(df.values)[:,1]) )
        
                
    return Pdelay


def dummy_train_cols():
    train_cols = ['Year',
                  'Month',
                  'DayOfMonth',
                  'DayOfWeek',
                  'ScheduledElapsedTime',
                  'Distance',
                  'DayOfYear',
                  'Week',
                  'ScheduledDepartureHour',
                  'ScheduledArrivalHour',
                  'DaysFromNearestHoliday',
                  'Carrier_AS',
                  'Carrier_B6',
                  'Carrier_CO',
                  'Carrier_DL',
                  'Carrier_F9',
                  'Carrier_FL',
                  'Carrier_MQ',
                  'Carrier_OO',
                  'Carrier_UA',
                  'Carrier_US',
                  'Carrier_VX',
                  'Carrier_WN',
                  'Carrier_XE',
                  'Carrier_YV',
                  'Destination_BOS',
                  'Destination_DEN',
                  'Destination_DFW',
                  'Destination_EWR',
                  'Destination_IAD',
                  'Destination_IAH',
                  'Destination_JFK',
                  'Destination_LAS',
                  'Destination_LAX',
                  'Destination_ORD',
                  'Destination_PDX',
                  'Destination_PHX',
                  'Destination_SAN',
                  'Destination_SBA',
                  'Destination_SEA',
                  'Destination_SLC',
                  'Destination_SNA']

    return train_cols
