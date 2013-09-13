from flask.ext.wtf import Form
from wtforms import SelectField, TextField
from wtforms.ext.dateutil.fields import DateField
from wtforms.validators import Required, Optional, Regexp
from datetime import datetime
import my_utils as mu

class LookingForFlightForm(Form):
    date = DateField('Date', validators = [Required()])
    origin = TextField('Origin', validators = [Required()])
    destination = TextField('Destination', validators = [Required()])

    
class AlreadyHaveAFlightForm(Form):
    date = DateField('Date', validators = [Required()])
    carrier = TextField('Carrier', validators = [Optional()])
    flightnumber = TextField('FlightNumber', validators = [Optional()])
