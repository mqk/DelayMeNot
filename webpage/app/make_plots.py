import numpy as np
import matplotlib.pyplot as plt

def delay_histogram(delays,pid=None):
    fig = plt.figure()
    ax = plt.axes([0.1,0.1,0.85,0.85])

    delays.plot(kind='bar', ax=ax, color='b', alpha=0.7)

    ax.set_xlabel('Delay [min]', size=16)
    ax.set_ylabel('Number of flights', size=16)

    pngname = 'plot.png'
    if pid is not None:
        pngname = 'plot_%s.png' % pid
    plt.savefig(pngname,dpi=150)
    
