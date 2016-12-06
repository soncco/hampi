var intimpa = intimpa || {};

(function($) {

  $.extend($.tablesorter.themes.bootstrap, {
    table      : 'table table-bordered',
    caption    : 'caption',
    header     : 'bootstrap-header',
    sortNone   : 'bootstrap-icon-unsorted',
    sortAsc    : 'icon-chevron-up glyphicon glyphicon-chevron-up',
    sortDesc   : 'icon-chevron-down glyphicon glyphicon-chevron-down',
  });

  $("#table").tablesorter({
    theme : "bootstrap",
    widthFixed: true,
    headerTemplate : '{content} {icon}',
    widgets : ["uitheme", "filter", "print"],
    widgetOptions : {
      filter_reset : ".reset",
    }
  })
  .tablesorterPager({
    container: $(".ts-pager"),
    cssGoto  : ".pagenum",
    removeRows: false,
    output: '{startRow} - {endRow} / {filteredRows} ({totalRows})',
    savePages: false
  });

})(jQuery)
