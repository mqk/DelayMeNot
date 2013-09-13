// add parser through the tablesorter addParser method 
$.tablesorter.addParser(
    { 
	// set a unique id 
	id: 'flightnumber', 
        is: function(s) { 
            // return false so this parser is not auto detected 
            return false; 
        }, 
	format: function(s) { 
            // format your data for normalization
            return s.match(/ +([0-9]*)/)[1];
	}, 
	// set type, either numeric or text 
	type: 'numeric' 
    }
);

$.tablesorter.addParser(
    {
	// set a unique id 
	id: 'departure_time', 
        is: function(s) { 
            // return false so this parser is not auto detected 
            return false; 
        }, 
	format: function(s) { 
            // format your data for normalization 
	    // alert(s.match(/ (.*M) /)[1]);
	    var times = s.match(/([0-1]?[0-9]:[0-5][0-9]\s(AM|PM))/g);
            return $.tablesorter.formatFloat(new Date("2000/01/01 " + times[0]).getTime());
	}, 
	// set type, either numeric or text 
	type: 'numeric' 
    }
);

$.tablesorter.addParser(
    {
	// set a unique id 
	id: 'arrival_time', 
        is: function(s) { 
            // return false so this parser is not auto detected 
            return false; 
        }, 
	format: function(s) { 
            // format your data for normalization 
	    var times = s.match(/([0-1]?[0-9]:[0-5][0-9]\s(AM|PM))/g);
	    // alert(times[times.length - 1]);
            return $.tablesorter.formatFloat(new Date("2000/01/01 " + times[times.length - 1]).getTime());
	}, 
	// set type, either numeric or text 
	type: 'numeric' 
    }
);

$.tablesorter.addParser(
    {
	// set a unique id 
	id: 'layover', 
        is: function(s) { 
            // return false so this parser is not auto detected 
            return false; 
        }, 
	format: function(s) { 
            // format your data for normalization 
	    // alert(s + ':' + s.match(/  ([0-9]*)/)[1] );
            return s.match(/  ([0-9]*)/)[1];
	}, 
	// set type, either numeric or text 
	type: 'numeric' 
    }
);
