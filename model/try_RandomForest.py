import numpy as np
import time, sys
import copy
from sklearn import ensemble

from summarize import summarize
import construct_datasets as cd

try:
    (data_train, data_test)
except NameError:
    (data_train, data_test) = cd.construct_datasets('EWR',min_year=2010,subsample=10)
    ## cd.save_to_pickle(data_train, data_test, 'test_dataset_fromEWR.pkl')

    ## (data_train, data_test) = cd.load_from_pickle('test_dataset_fromEWR_Year2010-2013_subsample=10.pkl')
    ## (data_train, data_test) = cd.load_from_pickle('test_dataset_fromEWR_Year1997-2013_subsample=10.pkl')
    ## (data_train, data_test) = cd.load_from_pickle('test_dataset_fromEWR_Year2010-2013.pkl')

        
### Training set columns
train_cols = list(data_train.columns)
train_cols.remove('ArrivalDelay')
## print train_cols


### Define training and test data set variables

late_delay = 30.0

X = data_train[train_cols].values.copy()
Y = np.zeros_like(data_train['ArrivalDelay'].values)
Y[data_train['ArrivalDelay'].values > late_delay] = 1

Xtest = data_test[train_cols].values.copy()
Ytest = np.zeros_like(data_test['ArrivalDelay'].values)
Ytest[data_test['ArrivalDelay'].values > late_delay] = 1


n_estimators = 1000
max_features = 55
## max_features = int(X.shape[1])
## max_features='auto'


print 'Constructing random forest classifier from training set...'
sys.stdout.flush()
time0 = time.time()
rfor = ensemble.RandomForestClassifier(n_estimators=n_estimators,max_features=max_features,n_jobs=-1)
rfor = rfor.fit(X, Y)
dt = time.time() - time0
print '   that took %.1f seconds.\n' % dt


Y_pred = rfor.predict(X)
## print 'Training sample:'
## summarize(Y,Y_pred)


Ytest_pred = rfor.predict(Xtest)
print 'Test sample:'
summarize(Ytest,Ytest_pred)

## del X,Y,Y_pred
## del Xtest,Ytest,Ytest_pred

## del rfor

