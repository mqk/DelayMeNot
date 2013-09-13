#!/usr/bin/python

import os    
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()
import matplotlib

from app import app
if __name__ == '__main__':
    app.run(debug=True)
