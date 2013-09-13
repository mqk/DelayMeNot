from flask import render_template, flash, redirect, request, url_for
from app import app
from forms import LookingForFlightForm, AlreadyHaveAFlightForm
import my_utils as mu


@app.route('/index', methods = ['GET', 'POST'])
@app.route('/', methods = ['GET', 'POST'])
def index():    

    form1 = LookingForFlightForm()
    form2 = AlreadyHaveAFlightForm()

    if form1.validate_on_submit():
        print ('       Date = "%s"' % form1.date.data)
        print ('     Origin = "%s"' % form1.origin.data)
        print ('Destination = "%s"' % form1.destination.data)

        
        return redirect(url_for('.results',
                                date=form1.date.data,
                                origin=form1.origin.data,
                                destination=form1.destination.data))

    if form2.validate_on_submit():
        print ('        Date = "%s"' % form2.date.data)
        print ('     Carrier = "%s"' % form2.carrier.data)
        print ('FlightNumber = "%s"' % form2.flightnumber.data)

        
        return redirect(url_for('.results',
                                date=form2.date.data,
                                carrier=form2.carrier.data,
                                flightnumber=form2.flightnumber.data))
    
    carrier_dict_name, _ = mu.read_carrier_dict()
    carriers = carrier_dict_name.values()
    return render_template('index.html', form1=form1, form2=form2, carriers=carriers)


@app.route('/results')
def results():
    import numpy as np
    from pandas import DataFrame
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap,rgb2hex,Normalize
    import datetime

    import get_flightstats as gfs
    import apply_RF_model as am
        
    ## cmap = plt.get_cmap('RdYlGn_r')
    cdict = {'red': ((0.0, 0.0, 0.0),
                     (1.0, 1.0, 1.0)),
            'green': ((0.0, 1.0, 1.0),
                      (1.0, 0.0, 0.0)),
            'blue': ((0.0, 0.0, 0.0),
                     (1.0, 0.0, 0.0))}
    cmap = LinearSegmentedColormap('my_colormap', cdict, 100)


    
    departure_date = datetime.datetime.strptime(request.args['date'], '%Y-%m-%d')
    departure_date_string = departure_date.strftime('%a, %b %d %Y')


    request_info = {'date':departure_date,
                    'date_string':departure_date_string}

    ### Looking to buy a flight
    if 'origin' in request.args.keys():
        request_info['mode'] = 0
        request_info['origin'] = request.args['origin']
        request_info['destination'] = request.args['destination']

    ### Already have a flight
    if 'carrier' in request.args.keys():
        request_info['mode'] = 1
        request_info['carrier'] = request.args['carrier']
        request_info['flightnumber'] = int(request.args['flightnumber'])

    fs_json = gfs.get_flightstats_json(request_info)
        
    flightstats = gfs.parse_flightstats_json(fs_json)
    flights = DataFrame( gfs.flatten_flightstats(flightstats) )

    Pdelay_dict_orig, Pdelay_dict_dest, model_summary_orig, model_summary_dest = am.apply_RF_model(flights,request_info['origin'],request_info['destination'])


    def assign_Pdelay(fid, Pdelay_dict_orig, Pdelay_dict_dest):
        if fid in Pdelay_dict_dest.keys():
            return Pdelay_dict_dest[fid]
        elif fid in Pdelay_dict_orig.keys():
            return Pdelay_dict_orig[fid]
        else:
            return -1.0
    
    color_norm = Normalize(0.0,0.5)
    
    for fs in flightstats:

        ### Pdelay = np.random.uniform(size=len(fs['FlightID']))

        Pdelay = [ assign_Pdelay(x, Pdelay_dict_orig, Pdelay_dict_dest) for x in fs['FlightID'] ]
        
        fs['IconColor'] = [rgb2hex( cmap(color_norm(x)) ) for x in Pdelay]
        fs['DelayProbability'] = ['%.1f%%' % (100.0*x) for x in Pdelay]


    ### model summaries
    model_summaries = {}

    if model_summary_orig:       
        importance, feature = zip(* sorted( zip(model_summary_orig['feature_importances'],model_summary_orig['training_columns']), reverse=True ) )
        model_summary_orig['top5_features'] = [(feature[i],importance[i]) for i in xrange(5)]
        model_summaries['origin'] = model_summary_orig

    if model_summary_dest:
        importance, feature = zip(* sorted( zip(model_summary_dest['feature_importances'],model_summary_dest['training_columns']), reverse=True ) )
        model_summary_dest['top5_features'] = [(feature[i],importance[i]) for i in xrange(5)]
        model_summaries['destination'] = model_summary_dest

    ### Render the page
    return render_template('results.html',
                           title='Results',
                           request_info=request_info,
                           flightstats=flightstats,
                           model_summaries=model_summaries)
    


@app.route('/test')
def test():
    return render_template('test.html')
