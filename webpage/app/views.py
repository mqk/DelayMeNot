from flask import render_template, flash, redirect, request, url_for
from app import app
from forms import FlightForm
import my_utils as mu

@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
def index():    

    form = FlightForm()

    if form.validate_on_submit():
        ## flash( ('     Origin = "%s"' % form.origin.data) )
        ## flash( ('Destination = "%s"' % form.destination.data) )
        ## flash( ('       Date = "%s"' % form.date.data) )

                
        print ('    Carrier = "%s"' % mu.carrier_dict[form.carrier.data])
        print ('     Origin = "%s"' % form.origin.data)
        print ('Destination = "%s"' % form.destination.data)
        print ('   DateTime = "%s"' % form.datetime.data)

        
        return redirect(url_for('.results',
                                carrier= form.carrier.data,
                                origin=form.origin.data,
                                destination=form.destination.data,
                                datetime=form.datetime.data))
                                       
    return render_template('index.html', form=form)


@app.route('/results')
def results():
    import db_access as dba
    from datetime import datetime

    departure_datetime = datetime.strptime(request.args['datetime'], '%Y-%m-%d %H:%M:%S')
    departure_date = departure_datetime.strftime('%a, %b %d %Y')
    departure_time = departure_datetime.strftime('%I:%M %p')
    
    ### flight_info is passed to render_template for results.html 
    flight_info = {'carrier':mu.carrier_dict[request.args['carrier']],
                   'origin':request.args['origin'],
                   'destination':request.args['destination'],
                   'departure_date':departure_date,
                   'departure_time':departure_time}

    
    ### Set up a flight from the date
    tmt = departure_datetime.timetuple()
    flight = {}
    flight['DateTime'] = departure_datetime
    flight['Carrier'] = request.args['carrier']
    flight['DayOfYear'] = tmt.tm_yday
    flight['Month'] = tmt.tm_mon
    flight['Week'] = tmt.tm_yday / 7
    flight['DayOfWeek'] = tmt.tm_wday + 1  ## Monday = 1
    flight['DepHour'] = tmt.tm_hour
    del tmt


    ### Connection to MySQL database
    db, cur = dba.connect()

    ### Retrieve all flights with the selected origin and destination
    df = dba.get_flights_from_route(cur, flight_info['origin'], flight_info['destination'])

    ### Calculate statistics
    dstats = dba.delay_statistics(flight, df)

    ### Close MySQL connection.
    dba.close_up(db, cur)


    """
    ### Hardwired, for development        
    import cPickle
    f = open('test.pkl','rb')
    dstats = cPickle.load(f)
    f.close()
    dstats.index.name = 'Grouping'
    """
    
    ### Sort dataframe into descending NumFlights order
    dstats = dstats.sort('NumFlights',ascending=False)
    groupings_order = [x for x in dstats.index]

    
    ### Turn it into a list of dicts, one element per row
    stats_info = [x[1].to_dict() for x in list(dstats.reset_index().iterrows())]

    ### get index (1-based) of "best" grouping (most restrictive with
    ### more than 100 flights)
    best_grouping = len(dstats[dstats['NumFlights'] > 100]['NumFlights'])
    print 'best grouping = %d' % best_grouping
    
    return render_template('results.html',
                           flight_info=flight_info,
                           stats_info=stats_info,
                           groupings_order=groupings_order,
                           best_grouping=best_grouping)


@app.route('/test')
def test():
    return render_template('test.html')
