from collections import OrderedDict

carrier_dict = OrderedDict()
carrier_dict['UA']='United Airlines'
carrier_dict['AA']='American Airlines'
carrier_dict['WN']='Southwest Airlines'
carrier_dict['DL']='Delta Airlines'
carrier_dict['US']='US Airways'
carrier_dict['NW']='Northwest Airlines'
carrier_dict['AS']='Alaska Airlines'


groupings = ['same DayOfWeek',
             'same DayOfWeek & Carrier',
             'same DepHour',
             'same Week',
             'same Week & Carrier',
             'same DepHour & Carrier',
             'same DayOfWeek & DepHour',
             'same Week & DayOfWeek','same Week & DayOfWeek & Carrier',
             'same DayOfWeek & DepHour & Carrier',
             'same Week & DepHour',
             'same Week & DepHour & Carrier',
             'same Week & DayOfWeek & DepHour & Carrier']
    
