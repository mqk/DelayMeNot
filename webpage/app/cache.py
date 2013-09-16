import cPickle
import os

def cache_results(request_info, flightstats, model_summaries):
    datestr = request_info['date'].strftime('%m%d%Y')

    if request_info['mode'] == 0:
        filename = './cached_results/results_%s_%s_%s.pkl' % (request_info['origin'],
                                                              request_info['destination'],
                                                              datestr)
    elif request_info['mode'] == 1:
        filename = './cached_results/results_%s_%s_%s.pkl' % (request_info['carrier'],
                                                              request_info['flightnumber'],
                                                              datestr)
    else:
        raise RuntimeError('Unknown request mode (%d)!' % request_info['mode'])

    print 'Saving results to cache file %s.' % filename
    
    f = open(filename,'wb')
    cPickle.dump((flightstats,model_summaries),f,2)
    f.close()


def get_cached_results(request_info):
    datestr = request_info['date'].strftime('%m%d%Y')

    
    if request_info['mode'] == 0:
        filename = './cached_results/results_%s_%s_%s.pkl' % (request_info['origin'],
                                                              request_info['destination'],
                                                              datestr)
    elif request_info['mode'] == 1:
        filename = './cached_results/results_%s_%s_%s.pkl' % (request_info['carrier'],
                                                              request_info['flightnumber'],
                                                              datestr)
    else:
        raise RuntimeError('Unknown request mode (%d)!' % request_info['mode'])

    if os.path.isfile(filename):
        print 'Loading previously calculated results from %s.' % filename

        f = open(filename,'rb')
        cached_results = cPickle.load(f)
        f.close()
    else:
        cached_results = None

    return cached_results

    
