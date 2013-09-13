import numpy as np

def summarize(Y,Ypred,quiet=False):
    error_rate = 1.0 - float(sum( Ypred == Y )) / len(Y)
    ind = (Y == 0)
    false_positive = 1.0 - float(sum( Ypred[ind] == Y[ind] )) / len(Y[ind])     ## on-time flights classified as late
    false_negative = 1.0 - float(sum( Ypred[~ind] == Y[~ind] )) / len(Y[~ind])  ## late flights classified as on-time
    precision = float(sum( Ypred[~ind] == Y[~ind] )) / sum( Ypred == 1 )
    recall = float(sum( Ypred[~ind] == Y[~ind] )) / sum( ~ind )

    F1 = 2.0 * precision*recall / (precision + recall)
    beta = 0.5
    Fhalf = (1+beta**2) * precision*recall / (beta**2 * precision + recall)
    beta = 2.0
    F2 = (1+beta**2) * precision*recall / (beta**2 * precision + recall)
    
    if not quiet:
        print '   Number of flights = %d' % len(Y)
        print '   Actual number of delayed flights = %d (%.1f%%)' % (sum(Y == 1),100.0*sum(Y==1)/len(Y))
        print '   Predicted number of delayed flights = %d (%.1f%%)' % (sum(Ypred == 1),100.0*sum(Ypred==1)/len(Y))
        print '   error rate = %.1f%%' % (100.0*error_rate)
        print '   false positive rate = %.1f%%' % (100.0*false_positive)
        print '   false negative rate = %.1f%%' % (100.0*false_negative)
        print '   precision = %.1f%%' % (100.0*precision)
        print '   recall = %.1f%%' % (100.0*recall)
        print '   (F_1,F_2,F_0.5) = (%.3f,%.3f,%.3f)' % (F1,F2,Fhalf)
        print

    result_struct = {
        'NumFlights':len(Y),
        'NumDelayedFlights':sum(Y == 1),
        'NumDelayedFlights_Predicted':sum(Ypred == 1),
        'ErrorRate':error_rate,
        'FalsePositiveRate':false_positive,
        'FalseNegativeRate':false_negative,
        'Precision':precision,
        'Recall':recall,
        'F_1':F1,
        'F_2':F2,
        'F_0.5':Fhalf}

    return result_struct

