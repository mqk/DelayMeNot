$("[rel='tooltip']").tooltip();

function show_grouping(row) {
    if( row == 0 ) {
	$('tbody#results_table tr').show()
    } else {
	$('tbody#results_table tr').hide()
	$('tbody#results_table tr#row'+(row-1)).show()
    }
}
