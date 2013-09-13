$("[rel='tooltip']").tooltip();

function show_grouping(row) {
    if( row == 0 ) {
	$('tbody#results_table tr').show()
    } else {
	$('tbody#results_table tr').hide()
	$('tbody#results_table tr#row'+(row-1)).show()
    }
}

$(document).ready(
    function() { 
	$("#results_table").tablesorter(
	    {
	    	headers: {
	    	    1: {sorter:'flightnumber'},
		    2: {sorter:'departure_time'},
		    3: {sorter:'arrival_time'},
		    5: {sorter:'layover'}
	    	}
	    }
	);
    }
); 
