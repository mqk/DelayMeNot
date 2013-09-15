import numpy as np
import time, sys, copy
import cPickle,gzip,subprocess

from sklearn import ensemble
from summarize import summarize

import construct_datasets as cd
import pandas as pd

def run_model(destination, subsample=None, min_Nflights=None):

    ### Unpickle datasets
    print 'Unpickling datasets...'
    time0 = time.time()
    filename = '/data/DelayMeNot/data/pickles_by_destination/datasets_%s.pkl' % destination
    (data_train, data_test) = cd.load_from_pickle(filename, gzip=True)
    print '   that took %.1f seconds.' % (time.time() - time0)


    ### subsample training data
    if subsample:
        if len(data_train) > 1e6:
            Nsub = int( float(len(data_train)) / 1e6 )
            data_train = data_train.ix[::Nsub]


    ### remove all routes with less than min_Nflights flights
    grouped = data_train.groupby('Origin')
    Nflights = grouped['Origin'].count()
    Nflights.sort(ascending=True)
    if min_Nflights:
        orig_list = list(Nflights[Nflights > min_Nflights].index)
        if len(orig_list) == 0:
            print 'Found no routes with more than %d flights!' % min_Nflights
            return 0
        data_train = data_train[data_train['Origin'].isin(orig_list)]
        data_test = data_test[data_test['Origin'].isin(orig_list)]
    else:
        orig_list = list(Nflights.index)

    ## return data_train, data_test
                
    ### "Dummify" the categorical 'Carrier' and 'Origin' columns,
    ### and add the dummies to the table, but drop the first dummy
    ### column to avoid "dummy variable trap".

    print 'Dummifying datasets...'
    time0 = time.time()

    dummies = pd.get_dummies(data_train['Carrier'],prefix='Carrier')
    data_train = data_train.join(dummies.ix[:,1:])
    dummies = pd.get_dummies(data_test['Carrier'],prefix='Carrier')
    data_test = data_test.join(dummies.ix[:,1:])

    dummies = pd.get_dummies(data_train['Origin'],prefix='Origin')
    data_train = data_train.join(dummies.ix[:,1:])
    dummies = pd.get_dummies(data_test['Origin'],prefix='Origin')
    data_test = data_test.join(dummies.ix[:,1:])

    ### Drop dummified columns
    data_train = data_train.drop(['Carrier','Origin'],axis=1)
    data_test = data_test.drop(['Carrier','Origin'],axis=1)
    
    print '   that took %.1f seconds.' % (time.time() - time0)
    
    ### Training set columns
    train_cols = list(data_train.columns)
    train_cols.remove('ArrivalDelay')
    
    ### Add any missing training columns to test dataset
    test_cols = list(data_test.columns)
    for tc in train_cols:
        if tc not in test_cols:
            data_test[tc] = np.zeros_like(data_test[test_cols[0]])
    
    ### Define training and test data set variables
    late_delay = 30.0

    X = data_train[train_cols].values.copy()
    Y = np.zeros_like(data_train['ArrivalDelay'].values)
    Y[data_train['ArrivalDelay'].values > late_delay] = 1

    Xtest = data_test[train_cols].values.copy()
    Ytest = np.zeros_like(data_test['ArrivalDelay'].values)
    Ytest[data_test['ArrivalDelay'].values > late_delay] = 1

    del data_train, data_test
    
    ### Train the RandomForest model
    ## n_estimators = 1000
    n_estimators = 128
    ## max_features = 'auto'
    max_features = int(X.shape[1]/2)
    
    print 'Constructing random forest classifier from training set...'
    print '   Number of flights in training data set = %d' % len(Y)
    sys.stdout.flush()
    time0 = time.time()
    rfor = ensemble.RandomForestClassifier(n_estimators=n_estimators,max_features=max_features,n_jobs=8)
    rfor = rfor.fit(X, Y)
    rfor.n_jobs = 1

    Y_pred = rfor.predict(X)
    train_summary = summarize(Y,Y_pred)

    dt_train = time.time() - time0
    print '   that took %.1f seconds.\n' % dt_train
    sys.stdout.flush()

    
    ### Test the model
    print 'Testing the model...'
    time0 = time.time()
    Ytest_pred = rfor.predict(Xtest)
    test_summary = summarize(Ytest,Ytest_pred)
    dt_test = (time.time() - time0)
    print '   that took %.1f seconds.' % dt_test
    sys.stdout.flush()

    
    ### Construct model summary dict
    model_summary = {}
    model_summary['training_columns'] = train_cols
    model_summary['training'] = train_summary
    model_summary['time_to_train'] = dt_train

    model_summary['test'] = test_summary
    model_summary['time_to_test'] = dt_test

    model_summary['late_delay'] = late_delay
    if subsample:
        model_summary['subsample'] = True
        model_summary['Nsub'] = Nsub
    else:
        model_summary['subsample'] = False
    model_summary['min_Nflights'] = min_Nflights
    model_summary['n_estimators'] = n_estimators
    model_summary['max_features'] = max_features

        
    ### Pickle the result
    print 'Pickling the result...'
    time0 = time.time()

    filename = '../RandomForest_models/by_destination/rfm_%s.pkl' % destination
    f = open(filename, 'wb')
    cPickle.dump((rfor,model_summary),f,2)
    f.close()
    subprocess.call('gzip %s' % filename, shell=True)
    print '   that took %.1f seconds.' % (time.time() - time0)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Train Random Forest model.')
    parser.add_argument('destination',
                        help='The 3-letter airport code of the destination')
    parser.add_argument('--subsample', action='store_true', default=False,
                        help='subsample the dataset')
    parser.add_argument('--min_Nflights', type=int, default=10000,
                        help='use only routes with more than min_Nflights flights')
    args = parser.parse_args()

    run_model(args.destination, subsample=args.subsample, min_Nflights=args.min_Nflights)
