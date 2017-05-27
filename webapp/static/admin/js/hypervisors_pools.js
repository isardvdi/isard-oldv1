/*
* Copyright 2017 the Isard-vdi project authors:
*      Josep Maria Viñolas Auquer
*      Alberto Larraz Dalmases
* License: AGPLv3
*/

$hypervisor_pool_template = $(".hyper-pool-detail");
$(document).ready(function() {
	$('#modalAddPool').on('hidden.bs.modal', function(){
        $(this).find('form')[0].reset();
        console.log('reset')
        slider_avgcpu.reset()
        slider_freqcpu.reset()
        slider_freemem.reset()
        slider_iowait.reset()
    });
    //~ $('[data-dismiss=modal]').on('click', function (e) {
        //~ var $t = $(this),
            //~ target = $t[0].href || $t.data("target") || $t.parents('.modal') || [];

      //~ $(target).find('form')[0].reset();
        //~ console.log('reset-close')
        //~ slider_avgcpu.reset()
        //~ slider_freqcpu.reset()
        //~ slider_freemem.reset()
        //~ slider_iowait.reset()
    //~ })
	$('.btn-new-pool').on('click', function () {
			$('#modalAddPool').modal({
				backdrop: 'static',
				keyboard: false
			}).modal('show');
				$("#weights-avg_cpu_idle-weight").ionRangeSlider({
						  type: "single",
						  min: 0,
						  max: 100,
                          from: 20,
                          step:5,
						  grid: true,
						  disable: false
						  }).data("ionRangeSlider").update();
                slider_avgcpu = $("#weights-avg_cpu_idle-weight").data("ionRangeSlider");
				$("#weights-cpu_freq-weight").ionRangeSlider({
						  type: "single",
						  min: 0,
						  max: 100,
                          step:5,
						  grid: true,
						  disable: false
						  }).data("ionRangeSlider").update();
                slider_freqcpu = $("#weights-cpu_freq-weight").data("ionRangeSlider");
				$("#weights-free_memory-weight").ionRangeSlider({
						  type: "single",
						  min: 0,
						  max: 100,
                          step:5,
						  grid: true,
						  disable: false
						  }).data("ionRangeSlider").update();
                slider_freemem = $("#weights-free_memory-weight").data("ionRangeSlider");
				$("#weights-io_wait_peaks-weight").ionRangeSlider({
						  type: "single",
						  min: 0,
						  max: 100,
                          step:5,
						  grid: true,
						  disable: false
						  }).data("ionRangeSlider").update();	
                slider_iowait = $("#weights-io_wait_peaks-weight").data("ionRangeSlider");
	});

    var tablepools = $('#hypervisors_pools').DataTable( {
        "ajax": {
            "url": "/admin/hypervisors_pools",
            "dataSrc": ""
        },
		"rowId": "id",
		"deferRender": false,
        "columns": [
				{
                "className":      'details-control',
                "orderable":      false,
                "data":           null,
                "width": "10px",
                "defaultContent": '<button class="btn btn-xs btn-info" type="button"  data-placement="top" ><i class="fa fa-plus"></i></button>'
				},
            { "data": "name"},
            { "data": "description"}]
    } );

	$('#hypervisors_pools').find('tbody').on('click', 'td.details-control', function () {
        var tr = $(this).closest('tr');
        var row = tablepools.row( tr );
		
        if ( row.child.isShown() ) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
        }
        else {
            // Open this row
            row.child( formatHypervisorPool(row.data()) ).show();
            data = row.data();
			$.each( data['paths'], function( k, v) {
				$.each( data['paths'][k], function( key, val ) {
					console.log(data['paths'][k])
					$('#hyper-pools-paths-'+data.id+' tbody').append('<tr><td>'+k+'</td><td>'+val['path']+'</td><td>'+val['disk_operations']+'</td><td>'+val['weight']+'</td></tr>');
				});
			});
			if(data['interfaces'].length==0){
				$('#hyper-pools-nets-'+data.id+' tbody').append('[All interfaces available for selection]')
			}else{
				$.each( data['interfaces'], function( k, v) {
					$.each( data['interfaces'][k], function( key, val ) {
						$('#hyper-pools-nets-'+data.id+' tbody').append('<tr><td>'+k+'</td><td>'+key+'</td><td>'+val['disk_operations']+'</td><td>'+val['weight']+'</td></tr>');
					});
				});
			}
            if(data['viewer']['certificate'].length >10){data['viewer']['certificate']='Yes';}
            $('#hyper-pools-viewer-'+data.id+' tbody').append('<tr><td>'+data['viewer']['defaultMode']+'</td><td>'+data['viewer']['domain']+'</td><td>'+data['viewer']['certificate']+'</td></tr>');
            tr.addClass('shown');
        }
    } );

});// document ready


function formatHypervisorPool ( d ) {
		$newPanel = $hypervisor_pool_template.clone();
		$newPanel.html(function(i, oldHtml){
			return oldHtml.replace(/d.id/g, d.id).replace(/d.name/g, d.name);
		});
		return $newPanel
}  



