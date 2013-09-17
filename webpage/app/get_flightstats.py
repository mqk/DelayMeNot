import numpy as np
import os
import json
import time
import datetime
import copy
import subprocess


def testit():
    ## departure_date = datetime.date(2013,10,14)
    departure_date = datetime.date(2013,10,15)
    departure_date_string = departure_date.strftime('%a, %b %d %Y')

    origin = 'SFO'
    destination = 'EWR'
    carrier = 'VX'
    flightnumber = '1178'

    mode = 0
        
    request_info = {'date':departure_date,
                    'date_string':departure_date_string,
                    'mode':mode}
                
    ### Looking to buy a flight
    if mode == 0:
        request_info['origin'] = origin
        request_info['destination'] = destination

    ### Already have a flight
    if mode == 1:
        request_info['carrier'] = carrier
        request_info['flightnumber'] = int(flightnumber)

    return get_flightstats_json(request_info)

        
def get_flightstats_json(request_info):
    datestr = request_info['date'].strftime('%m%d%Y')
    date_year = request_info['date'].year
    date_month = request_info['date'].month
    date_day = request_info['date'].day


    ### If carrier-flightnumber mode, first make an API to get the
    ### origin and destination
    if request_info['mode'] == 1:
        json_filename = 'JSON/%s_%s_%s.json' % (request_info['carrier'],
                                                request_info['flightnumber'],
                                                datestr)
        if os.path.isfile(json_filename):
            print 'Using previously downloaded JSON file %s.' % json_filename
        else:
            print 'Using FlightStats API to get JSON, saving it to %s.' % json_filename

            API_string = 'https://api.flightstats.com/flex/schedules/rest/v1/json/flight/%s/%d/departing/%d/%d/%d?appId=06c64b04&appKey=eb5577593bd351d764478d64d535258d' % (request_info['carrier'],request_info['flightnumber'],date_year,date_month,date_day)
            command_list = ['curl','-v','-o',json_filename,'-X','GET',API_string]

            ## curl_command = 'curl -v  -o %s -X GET "https://api.flightstats.com/flex/schedules/rest/v1/json/flight/%s/%d/departing/%d/%d/%d?appId=06c64b04&appKey=eb5577593bd351d764478d64d535258d" &> %s.log' % (json_filename,request_info['carrier'],request_info['flightnumber'],date_year,date_month,date_day,json_filename)
            print 'Executing this curl command:\n   ', ' '.join(command_list)
            
            time0 = time.time()
            logf = open(json_filename+'.log','w')
            subprocess.call(command_list, stdout=logf, stderr=subprocess.STDOUT)
            logf.close()
            print '   That took %.1f seconds.' % (time.time() - time0)

        f = open(json_filename,'r')
        flightschedule_json = json.load(f)
        f.close()

        request_info['origin'] = flightschedule_json['scheduledFlights'][0]['departureAirportFsCode']
        request_info['destination'] = flightschedule_json['scheduledFlights'][0]['arrivalAirportFsCode']
            
    ### end of 'if request_info['mode'] == 1:'


    ### Get the flightstats for destination-origin
    
    json_filename = 'JSON/%s_%s_%s.json' % (request_info['origin'],
                                            request_info['destination'],
                                            datestr)
    if os.path.isfile(json_filename):
        print 'Using previously downloaded JSON file %s.' % json_filename
    else:
        print 'Using FlightStats API to get JSON, saving it to %s.' % json_filename

        API_string = 'https://api.flightstats.com/flex/connections/rest/v1/json/connecting/from/%s/to/%s/departing/%d/%d/%d?appId=06c64b04&appKey=eb5577593bd351d764478d64d535258d' % (request_info['origin'],request_info['destination'],date_year,date_month,date_day)
        command_list = ['curl','-v','-o',json_filename,'-X','GET',API_string]
            
        ## curl_command = 'curl -v -o %s -X GET "https://api.flightstats.com/flex/connections/rest/v1/json/connecting/from/%s/to/%s/departing/%d/%d/%d?appId=06c64b04&appKey=eb5577593bd351d764478d64d535258d" > %s.log 2>&1' % (json_filename,request_info['origin'],request_info['destination'],date_year,date_month,date_day,json_filename)
        print 'Executing this curl command:\n   ', ' '.join(command_list)
            
        time0 = time.time()
        logf = open(json_filename+'.log','w')
        subprocess.call(command_list, stdout=logf, stderr=subprocess.STDOUT)
        logf.close()
        print '   That took %.1f seconds.' % (time.time() - time0)
            
    f = open(json_filename,'r')
    flightstats_json = json.load(f)
    f.close()

    return flightstats_json

    
def parse_flightstats_json(flightstats_json):

    carrier_dict = {x['fs']:x['name'] for x in flightstats_json['appendix']['airlines']}

    flights = flightstats_json['flights']
    Nflights = len(flights)

    flightstats = []

    for i,f in enumerate(flights):

        ## not sure if this is necessary, are more than 2 legs ever returned?
        if len(f['flightLegs']) > 2: continue

        Nlegs = len(f['flightLegs'])
        
        this_flight = {}
        this_flight['Nlegs'] = Nlegs
        this_flight['InitialOrigin'] = f['departureAirportFsCode']
        this_flight['FinalDestination'] = f['arrivalAirportFsCode']

        this_flight['FlightID'] = []
        
        this_flight['Origin'] = []
        this_flight['Destination'] = []
        this_flight['Carrier'] = []
        this_flight['CarrierCode'] = []
        this_flight['FlightNumber'] = []
        this_flight['FlightDuration'] = []
        this_flight['Distance'] = []
        
        this_flight['DepartureDateTime'] = []
        this_flight['DepartureDate'] = []
        this_flight['DepartureTime'] = []
        this_flight['DepartureDateAdjustment'] = []

        this_flight['ArrivalDateTime'] = []
        this_flight['ArrivalDate'] = []
        this_flight['ArrivalTime'] = []
        this_flight['ArrivalDateAdjustment'] = []

        
        for leg in f['flightLegs']:
            this_flight['Origin'].append(leg['departureAirportFsCode'] )
            this_flight['Destination'].append(leg['arrivalAirportFsCode'] )
            this_flight['Carrier'].append( carrier_dict[leg['carrierFsCode']] )
            this_flight['CarrierCode'].append( leg['carrierFsCode'] )
            this_flight['FlightNumber'].append( int(leg['flightNumber']) )
            this_flight['FlightID'].append( leg['carrierFsCode']+'-'+leg['flightNumber'] )
            this_flight['FlightDuration'].append( leg['flightDurationMinutes'] )
            this_flight['Distance'].append( leg['distanceMiles'] )

            this_flight['DepartureDateAdjustment'].append( leg['departureDateAdjustment'] )
            this_datetime = datetime.datetime.strptime(flightstats_json['request']['date']['interpreted']+' '+leg['departureTime'][:-4],'%Y-%m-%d %H:%M:%S')
            if leg['departureDateAdjustment']:
                this_datetime += datetime.timedelta(days=1)
            this_flight['DepartureDateTime'].append( this_datetime )
            this_flight['DepartureDate'].append( this_datetime.strftime('%m/%d/%Y') )
            this_flight['DepartureTime'].append( this_datetime.strftime('%I:%M %p') )

            this_flight['ArrivalDateAdjustment'].append( leg['arrivalDateAdjustment'] )
            this_datetime = datetime.datetime.strptime(flightstats_json['request']['date']['interpreted']+' '+leg['arrivalTime'][:-4],'%Y-%m-%d %H:%M:%S')
            if leg['arrivalDateAdjustment']:
                this_datetime += datetime.timedelta(days=1)
            this_flight['ArrivalDateTime'].append( this_datetime )
            this_flight['ArrivalDate'].append( this_datetime.strftime('%m/%d/%Y') )
            this_flight['ArrivalTime'].append( this_datetime.strftime('%I:%M %p') )


        if Nlegs > 1:
            this_flight['ConnectionAirport'] = f['flightLegs'][0]['arrivalAirportFsCode']
            this_flight['LayoverMinutes'] = f['layoverDurationMinutes']
        else:
            this_flight['ConnectionAirport'] = '-'
            this_flight['LayoverMinutes'] = '-'
            
        flightstats.append(this_flight)

    return flightstats

def flatten_flightstats(flightstats):
    keys = flightstats[0].keys()
    keys_to_drop = ['ConnectionAirport', 'FinalDestination', 'InitialOrigin', 'LayoverMinutes', 'Nlegs']
    for k in keys_to_drop:
        keys.remove(k)

    flattened = []
    for f in flightstats:
        
        for i in xrange(f['Nlegs']):
            newf = {k:f[k][i] for k in keys}
            flattened.append(newf)

    return flattened
