var intimpa = intimpa || {};

(function($) {
  $.fn.editable.defaults.emptytext = 'Vacío';
  $('.editable').editable({
    type: 'text',
    pk: the_pk,
    url: '/venta/editar/'
  });

  $('.editable-date').editable({
    type: 'date',
    format: 'yyyy-mm-dd',
    viewformat: 'dd/mm/yyyy',
    pk: the_pk,
    url: '/venta/editar/'
  });
})(jQuery)
