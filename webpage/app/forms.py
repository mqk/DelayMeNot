from flask.ext.wtf import Form
from wtforms import SelectField, TextField, IntegerField
from wtforms.ext.dateutil.fields import DateField
from wtforms.validators import Required, Optional, NumberRange, Regexp, AnyOf
from datetime import datetime
import my_utils as mu

class LookingForFlightForm(Form):

    airport_dict_name, _ = mu.read_airport_dict()
    airports = ['%s - %s' % (v,k) for k,v in airport_dict_name.iteritems()]
    airport_values = airport_dict_name.keys() + airport_dict_name.values() + airports
    airport_validator = AnyOf(airport_values, message=u'Invalid input, must be an airport name.')
    
    date = DateField('Date', validators = [Required()])
    origin = TextField('Origin', validators = [Required(),airport_validator])
    destination = TextField('Destination', validators = [Required(),airport_validator])
    
class AlreadyHaveAFlightForm(Form):

    carrier_dict_name, _ = mu.read_carrier_dict()
    carriers = ['%s - %s' % (v,k) for k,v in carrier_dict_name.iteritems()]
    carrier_values = carrier_dict_name.keys() + carrier_dict_name.values() + carriers
    carrier_validator = AnyOf(carrier_values, message=u'Invalid input, must be a carrier name.')
    
    date = DateField('Date', validators = [Required()])
    carrier = TextField('Carrier', validators = [Required(),carrier_validator])
    flightnumber = IntegerField('FlightNumber', validators = [Required(message=u'This field is required, and must be an integer.'),NumberRange(min=1, message=u'Invalid input, must be greater than zero.')])
