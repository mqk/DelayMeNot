$("[rel='tooltip']").tooltip();

function show_filtered_table_rows() {
    /* Get rid of .visible for all rows. */
    $('#results_table_body tr').removeClass("visible");

    /* If the filter div has class .carrier_All, then add class
     * .visible to all rows. */
    if ($('#filters').hasClass("carrier_All")) {
        $('#results_table_body tr').addClass("visible");
    }
    /* If it doesn't, then check for the existence of individual
     * carriers in the class, and add .visible to matching rows. */
    else {
        var classList =$('#filters').attr('class').split(/\s+/);
        $.each( classList, function(index, item){
            var pos = item.indexOf('carrier_');
            if ( pos != -1) {
                var carrier = item.substring(pos+8);
                $('#results_table_body tr.'+carrier).addClass("visible");
            }
        });
    }

    /* Check for the presence of the online_only filter, and if set
     * remove .visible for all rows with class .offline. */
    if ($('#filters').hasClass("online_only")) {
        $('#results_table_body tr.offline').removeClass("visible");
    }

    /* Check for the presence of the nonstop_only (or withstop_only)
     * filters, and if set remove .visible for all rows with class
     * .withstop (or .non-stop). */
    if ($('#filters').hasClass("nonstop_only")) {
        $('#results_table_body tr.withstop').removeClass("visible");
    }
    else if ($('#filters').hasClass("withstop_only")) {
        $('#results_table_body tr.non-stop').removeClass("visible");
    }

    /* Hide all rows, then show those with class .visible. */
    $('#results_table_body tr').hide();
    $('#results_table_body tr.visible').show();
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
	    	},
                sortList: [[2,0]]
	    }
	);

        /*
        $("#toggle_animation").click(function() {    
            $(".jumbotron").css('-webkit-animation-play-state', function(i, v) {
                return v === 'paused' ? 'running' : 'paused';        
            });

            $(this).toggleClass('icon-pause icon-play');
        });
        */

        $('#carrier_all').click(function() {
            $(this).addClass("toggled-on");
            $('.carrier_single').removeClass("toggled-on");

            /* Remove all carrier_* classes from #filters. */
            var classList =$('#filters').attr('class').split(/\s+/);
            $.each( classList, function(index, item){
                if ( item.indexOf('carrier_') != -1) {
                    $('#filters').removeClass(item);
                }
            });

            $('#filters').addClass("carrier_All");

            show_filtered_table_rows();
        });

        $('.carrier_single').click(function() {
            /*  get the name of the selected carrier */
            var carrier = $(this).attr('class').split(/\s+/);

            $(this).toggleClass("toggled-on");
            $('#filters').toggleClass(carrier[1]);

            /* If it was toggled on, then remove .toggled-on from
             * #carrier_all, ... */
            if ($(this).hasClass("toggled-on")) {
                $('#carrier_all').removeClass("toggled-on");
                $('#filters').removeClass("carrier_All");
            } 
            /* ... if it was toggled off, then check to see if any
             * individual carriers are left in the filter class, and
             * if not then add .carrier_All to the filters and toggle
             * #carrier_all to on. */
            else {
                var count=0;
                var classList =$('#filters').attr('class').split(/\s+/);
                $.each( classList, function(index, item){
                    if ( item.indexOf('carrier_') != -1) {
                        count += 1;
                    }
                });
                if (count == 0) {
                    $('#filters').addClass("carrier_All");
                    $('#carrier_all').addClass("toggled-on");
                }
            }

            show_filtered_table_rows();
        });

        $('#carrier_on-line').click(function() {
            $(this).toggleClass("toggled-on");
            $('#filters').toggleClass("online_only");

            show_filtered_table_rows();
        });

        $('#connections_nonstop').click(function() {
            $(this).toggleClass("toggled-on");
            $('#filters').toggleClass("nonstop_only");

            if ($(this).hasClass("toggled-on")) {
                $('#connections_withstop').removeClass("toggled-on");
                $('#filters').removeClass("withstop_only");
            }

            show_filtered_table_rows();
        });

        $('#connections_withstop').click(function() {
            $(this).toggleClass("toggled-on");
            $('#filters').toggleClass("withstop_only");

            if ($(this).hasClass("toggled-on")) {
                $('#connections_nonstop').removeClass("toggled-on");
                $('#filters').removeClass("nonstop_only");
            }

            show_filtered_table_rows();
        });

        $('#static_results_next').click(function() {
            if ($(".static_result").hasClass("image1")) {
                $(".static_result").toggleClass("image1 image2");
                $(".static_result").attr("src","/static/img/results2.png");

                $("#static_results_prev").show();
                $("#static_results_next").show();
            } else if ($(".static_result").hasClass("image2")) {
                $(".static_result").toggleClass("image2 image3");
                $(".static_result").attr("src","/static/img/results3.png");

                $("#static_results_next").hide();
            }
        });

        $('#static_results_prev').click(function() {
            if ($(".static_result").hasClass("image2")) {
                $(".static_result").toggleClass("image2 image1");
                $(".static_result").attr("src","/static/img/results1.png");

                $("#static_results_prev").hide();
            } else if ($(".static_result").hasClass("image3")) {
                $(".static_result").toggleClass("image3 image2");
                $(".static_result").attr("src","/static/img/results2.png");

                $("#static_results_prev").show();
                $("#static_results_next").show();
            }
        });


    }
); 
