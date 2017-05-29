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

                $('.paths-tags').select2({
                    tags: true,
                    tokenSeparators: [",", " "]
                }).on("change", function(e) {
                    var isNew = $(this).find('[data-select2-tag="true"]');
                    if(isNew.length){
                        isNew.replaceWith('<option selected value="'+isNew.val()+'">'+isNew.val()+'</option>');
                        $.ajax({
                            // ... store tag ...
                        });
                    }
                });
                
                
                                            //~ <input id="table_diskop" placeholder="" type="text">
                                            //~ <input id="table-weights" class="form-control col-md-7 col-xs-12 weight-slider" type="text">
            
                table_paths = $('#table_paths').DataTable();
                $('#test').on('click', function () {
                    console.log('in')
                    //~ $('#table_paths tbody').append('<tr><th><input id="table_paths" name="table_paths" placeholder="Absolute path (/isard/bases)" type="text" value="/isard/bases"> \
                                            //~ </th><th>2</th><th>3</th><th>4</th></tr>');
                        console.log('add or update')
                        var data = JSON.parse({'path':'/isard','disk_operations':'localhost','weight':100});
                        table_paths.row.add(data).draw();
                        //~ if($("#" + data.id).length == 0) {
                          //~ //it doesn't exist
                          //~ table.row.add(data).draw();
                        //~ }else{
                          //~ //if already exists do an update (ie. connection lost and reconnect)
                          //~ var row = table.row('#'+data.id); 
                          //~ table.row(row).data(data).invalidate();			
                        //~ }
                        //~ table.draw(false);
                    //~ });
                    //~ var text = JSON.stringify($('#hypervisors').data().toArray(), null, '\t');
                    //~ $.each(table.rows({filter: 'applied'}).data(),function(key, value){
                        //~ console.log(value['name']+value['id'])
                    //~ });
                    console.log(JSON.stringify(table_paths.rows({filter: 'applied'}).data().toArray()))
                });
            
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

				$(".weight-slider").ionRangeSlider({
						  type: "single",
						  min: 0,
						  max: 100,
                          step:5,
						  grid: true,
						  disable: false
						  }).data("ionRangeSlider").update();	
                $('.hyper-list').select2({
                  multiple: true,
                  ajax: {
                    url: "/admin/hypervisors/json",
                    dataType: 'json',
                    delay: 250,
                    data: function (params) {
                      return {
                        q: params.id, // search term
                        page: params.page
                      };
                    },
                    processResults: function (data, page) {
                      // parse the results into the format expected by Select2.
                      // since we are using custom formatting functions we do not need to
                      // alter the remote JSON data
                           console.log(data);
                      return {
                       
                        results: data.id
                      };
                    },
                    cache: true
                  },
                 escapeMarkup: function (markup) { return markup; },
                    minimumInputLength: 1,
                    //~ templateResult: formatRepo,
                    //~ templateSelection: formatRepoSelection

                });
                
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




//// Parse table
/**
 * table-to-json
 * jQuery plugin that reads an HTML table and returns a javascript object representing the values and columns of the table
 *
 * @author Daniel White
 * @copyright Daniel White 2017
 * @license MIT <https://github.com/lightswitch05/table-to-json/blob/master/MIT-LICENSE>
 * @link https://github.com/lightswitch05/table-to-json
 * @module table-to-json
 * @version 0.11.1
 */
(function( $ ) {
  'use strict';

  $.fn.tableToJSON = function(opts) {

    // Set options
    var defaults = {
      ignoreColumns: [],
      onlyColumns: null,
      ignoreHiddenRows: true,
      ignoreEmptyRows: false,
      headings: null,
      allowHTML: false,
      includeRowId: false,
      textDataOverride: 'data-override',
      extractor: null,
      textExtractor: null
    };
    opts = $.extend(defaults, opts);

    var notNull = function(value) {
      return value !== undefined && value !== null;
    };

    var ignoredColumn = function(index) {
      if( notNull(opts.onlyColumns) ) {
        return $.inArray(index, opts.onlyColumns) === -1;
      }
      return $.inArray(index, opts.ignoreColumns) !== -1;
    };

    var arraysToHash = function(keys, values) {
      var result = {}, index = 0;
      $.each(values, function(i, value) {
        // when ignoring columns, the header option still starts
        // with the first defined column
        if ( index < keys.length && notNull(value) ) {
          result[ keys[index] ] = value;
          index++;
        }
      });
      return result;
    };

    var cellValues = function(cellIndex, cell, isHeader) {
      var $cell = $(cell),
        // extractor
        extractor = opts.extractor || opts.textExtractor,
        override = $cell.attr(opts.textDataOverride),
        value;
      // don't use extractor for header cells
      if ( extractor === null || isHeader ) {
        return $.trim( override || ( opts.allowHTML ? $cell.html() : cell.textContent || $cell.text() ) || '' );
      } else {
        // overall extractor function
        if ( $.isFunction(extractor) ) {
          value = override || extractor(cellIndex, $cell);
          return typeof value === 'string' ? $.trim( value ) : value;
        } else if ( typeof extractor === 'object' && $.isFunction( extractor[cellIndex] ) ) {
          value = override || extractor[cellIndex](cellIndex, $cell);
          return typeof value === 'string' ? $.trim( value ) : value;
        }
      }
      // fallback
      return $.trim( override || ( opts.allowHTML ? $cell.html() : cell.textContent || $cell.text() ) || '' );
    };

    var rowValues = function(row, isHeader) {
      var result = [];
      var includeRowId = opts.includeRowId;
      var useRowId = (typeof includeRowId === 'boolean') ? includeRowId : (typeof includeRowId === 'string') ? true : false;
      var rowIdName = (typeof includeRowId === 'string') === true ? includeRowId : 'rowId';
      if (useRowId) {
        if (typeof $(row).attr('id') === 'undefined') {
          result.push(rowIdName);
        }
      }
      $(row).children('td,th').each(function(cellIndex, cell) {
        result.push( cellValues(cellIndex, cell, isHeader) );
      });
      return result;
    };

    var getHeadings = function(table) {
      var firstRow = table.find('tr:first').first();
      return notNull(opts.headings) ? opts.headings : rowValues(firstRow, true);
    };

    var construct = function(table, headings) {
      var i, j, len, len2, txt, $row, $cell,
        tmpArray = [], cellIndex = 0, result = [];
      table.children('tbody,*').children('tr').each(function(rowIndex, row) {
        if( rowIndex > 0 || notNull(opts.headings) ) {
          var includeRowId = opts.includeRowId;
          var useRowId = (typeof includeRowId === 'boolean') ? includeRowId : (typeof includeRowId === 'string') ? true : false;

          $row = $(row);

          var isEmpty = ($row.find('td').length === $row.find('td:empty').length) ? true : false;

          if( ( $row.is(':visible') || !opts.ignoreHiddenRows ) && ( !isEmpty || !opts.ignoreEmptyRows ) && ( !$row.data('ignore') || $row.data('ignore') === 'false' ) ) {
            cellIndex = 0;
            if (!tmpArray[rowIndex]) {
              tmpArray[rowIndex] = [];
            }
            if (useRowId) {
              cellIndex = cellIndex + 1;
              if (typeof $row.attr('id') !== 'undefined') {
                tmpArray[rowIndex].push($row.attr('id'));
              } else {
                tmpArray[rowIndex].push('');
              }
            }

            $row.children().each(function(){
              $cell = $(this);
              // skip column if already defined
              while (tmpArray[rowIndex][cellIndex]) { cellIndex++; }

              // process rowspans
              if ($cell.filter('[rowspan]').length) {
                len = parseInt( $cell.attr('rowspan'), 10) - 1;
                txt = cellValues(cellIndex, $cell);
                for (i = 1; i <= len; i++) {
                  if (!tmpArray[rowIndex + i]) { tmpArray[rowIndex + i] = []; }
                  tmpArray[rowIndex + i][cellIndex] = txt;
                }
              }
              // process colspans
              if ($cell.filter('[colspan]').length) {
                len = parseInt( $cell.attr('colspan'), 10) - 1;
                txt = cellValues(cellIndex, $cell);
                for (i = 1; i <= len; i++) {
                  // cell has both col and row spans
                  if ($cell.filter('[rowspan]').length) {
                    len2 = parseInt( $cell.attr('rowspan'), 10);
                    for (j = 0; j < len2; j++) {
                      tmpArray[rowIndex + j][cellIndex + i] = txt;
                    }
                  } else {
                    tmpArray[rowIndex][cellIndex + i] = txt;
                  }
                }
              }

              txt = tmpArray[rowIndex][cellIndex] || cellValues(cellIndex, $cell);
              if (notNull(txt)) {
                tmpArray[rowIndex][cellIndex] = txt;
              }
              cellIndex++;
            });
          }
        }
      });
      $.each(tmpArray, function( i, row ){
        if (notNull(row)) {
          // remove ignoredColumns / add onlyColumns
          var newRow = notNull(opts.onlyColumns) || opts.ignoreColumns.length ?
            $.grep(row, function(v, index){ return !ignoredColumn(index); }) : row,

            // remove ignoredColumns / add onlyColumns if headings is not defined
            newHeadings = notNull(opts.headings) ? headings :
              $.grep(headings, function(v, index){ return !ignoredColumn(index); });

          txt = arraysToHash(newHeadings, newRow);
          result[result.length] = txt;
        }
      });
      return result;
    };

    // Run
    var headings = getHeadings(this);
    return construct(this, headings);
  };
})( jQuery );



