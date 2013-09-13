import cPickle
import time, os
import datetime
import numpy as np
import pandas as pd
from pandas import DataFrame

hdf = pd.read_fwf('data/US_holidays_1997-2020.txt',colspecs=[[0,2],[3,5],[6,10],[12,50]],header=None,names=['Month','Day','Year','Holiday'])
hdf['Holiday'] = hdf['Holiday'].apply(lambda x: x[:-1])
holiday_dates = hdf.apply(lambda x: datetime.date(x['Year'],x['Month'],x['Day']),axis=1).values
del hdf
    
def apply_RF_model(flights, origin, destination):
    """
    flights is a DataFrame.
    """

    ### *** Origin model ***
    Pdelay_orig = {}

    filename = 'RandomForest_models/by_origin/rfm_%s.pkl' % origin
    if os.path.isfile(filename):
        
        print 'Unpickling RandomForest model for Origin...'
        time0 = time.time()       
        f = open(filename, 'rb')
        (rfor,model_summary_orig) = cPickle.load(f)
        f.close()
        print '   That took %.1f seconds.' % (time.time() - time0)

        ## add feature importance to models
        model_summary_orig['feature_importances'] = rfor.feature_importances_
        
        ### set to single core for model evaluation
        rfor.n_jobs = 1
    
        train_cols = model_summary_orig['training_columns']
    
        ### Create Origin flights DataFrame        
        df = flights[ flights['Origin'] == origin ]
        df, FlightID = fill_dataframe(df,train_cols)
        
        ### at last, apply the model
        Pdelay_orig = dict( zip(FlightID, rfor.predict_proba(df.values)[:,1]) )
    
        del df, FlightID, rfor
    else:
        print 'Could not find Origin model (%s), skipping.' % filename

    ### *** Destination model ***
    Pdelay_dest = {}
    model_summary_dest = {}
    
    filename = 'RandomForest_models/by_destination/rfm_%s.pkl' % destination
    if os.path.isfile(filename):
        
        print 'Unpickling RandomForest model for Destination...'
        time0 = time.time()       
        f = open(filename, 'rb')
        (rfor,model_summary_dest) = cPickle.load(f)
        f.close()
        print '   That took %.1f seconds.' % (time.time() - time0)

        ## add feature importance to models
        model_summary_dest['feature_importances'] = rfor.feature_importances_

        ### set to single core for model evaluation
        rfor.n_jobs = 1

        train_cols = model_summary_dest['training_columns']
    
        ### Create Destination flights DataFrame        
        df = flights[ flights['Destination'] == destination ]
        df, FlightID = fill_dataframe(df,train_cols)
    
        ### at last, apply the model
        Pdelay_dest = dict( zip(FlightID, rfor.predict_proba(df.values)[:,1]) )

        del df, FlightID, rfor
    else:
        print 'Could not find Destination model (%s), skipping.' % filename

    
    return Pdelay_orig, Pdelay_dest, model_summary_orig, model_summary_dest


def fill_dataframe(df, train_cols):
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
    
    return df, FlightID


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
