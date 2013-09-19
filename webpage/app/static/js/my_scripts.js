$("[rel='tooltip']").tooltip();

$(document).ready(
    function() { 
	$("#results_table").tablesorter(
	    {
	    	headers: {
	    	    1: {sorter:'flightnumber'},
		    2: {sorter:'departure_time'},
		    3: {sorter:'arrival_time'},
		    5: {sorter:'layover'}
	    	},
                sortList: [[2,0]]
	    }
	);

        $('#carrier_all').click(function() {
            $('#results_table_body tr').show();
        });

        $('#carrier_on-line').click(function() {
            $('#results_table_body tr').hide();
            $('#results_table_body tr.online').show();
        });

        $('.carrier_single').click(function() {
            var carrier = $(this).html();
            var rex =  new RegExp(carrier);
            $('#results_table_body tr').hide();
            $('#results_table_body tr').filter(function() {
                return rex.test($(this).text());
            }).show();
        });

        $('#connections_all').click(function() {
            $('#results_table_body tr').show();
        });

        $('#connections_direct').click(function() {
            $('#results_table_body tr').hide();
            $('#results_table_body tr.direct').show();
        });

        $('#connections_withstop').click(function() {
            $('#results_table_body tr').hide();
            $('#results_table_body tr.withstop').show();
        });

    }
); 
