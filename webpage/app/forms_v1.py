from flask.ext.wtf import Form
from wtforms import SelectField, TextField
from wtforms.ext.dateutil.fields import DateTimeField
from wtforms.validators import Required, Optional, Regexp
from datetime import datetime
import my_utils as mu

class FlightForm(Form):

    
    choices = [('', 'Select Airline')] + [(k,v) for k,v in mu.carrier_dict.iteritems()]

    carrier = SelectField('Carrier', validators = [Required()],
                          id='myselect',
                          choices=choices )

    
    origin = TextField('Origin', validators = [Required()])
    destination = TextField('Destination', validators = [Required()])

    now = datetime.now()
    default_datetime = datetime(now.year, now.month, now.day, 10, 0)
    datetime = DateTimeField('DateTime', parse_kwargs={'default':default_datetime}, validators = [Required()])

    ## import re
    ## regex = re.compile('^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$')
    ## time = TextField('Time', validators = [Optional(), Regexp(regex)])
    
