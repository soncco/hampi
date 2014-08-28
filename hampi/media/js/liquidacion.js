var intimpa = intimpa || {};

(function($) {
  $('.print').click(function() {
    almacen = $('#almacen').val();
    fecha = $('#fechapost').val();
    user = $('#user').val();
    location.href = '/liquidacion/print/' + fecha + '/' + almacen + '/' + user;
  });

})(jQuery)
