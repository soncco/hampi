var intimpa = intimpa || {};

(function($) {

  var acProductoNuevo = {
    minLength: 1,
    source: function(request, response) {
      $.ajax({
        url: '/api/productos-filter/',
        dataType: 'json',
        data: {
          term: request.term
        },
        success: function(data, e, xhr) {
          if(e)
          response($.map(data, function (item) {
            return {
              data: item,
              label: item.producto + ' '
                + item.marca + ' - '
                + item.comercial,
              value: item.producto + ' '
                + item.marca + ' - '
                + item.comercial
            }
          }));
        }
      })
    },
    response: function(e, ui) {
      if(ui.content.length === 0) {
        alert('El producto no existe, intenta agregar el producto');
        var parent = $(e.target).parent();
        parent.find('.ac-producto').val('');
      }
    },
    select: function(e, ui) {
      $('#producto-nuevo-id').val(ui.item.data.id);
    },
    change: function(e,ui) {
      if(!ui.item) {
        alert('El producto no existe, intenta agregar el producto');
        var parent = $(e.target).parent();
        parent.find('.ac-producto').val('');
      }
    }
  };

  $('.ac-producto').autocomplete(acProductoNuevo);
  $('.ac-producto').autocomplete( "option", "appendTo", ".eventInsForm" );

  $('.ac-producto').change(function() {
    if($(this).val() === '') {
      $('#producto-nuevo-id').val('');
    }
  });

  $('.add-product').click(function() {
    $('#productLoteModal').modal('hide');
    $('#productModal').modal({show: true});
  });

  $('.add-product-lote').click(function() {
    $('#productModal').modal('hide');
    $('#productLoteModal').modal({show: true});
  });

  $('#productModal form').submit(function(e) {
    e.preventDefault();
    $.ajax({
      'url': $(this).attr('action'),
      'type': 'POST',
      'data': $('#productModal form input').serialize(),
      'success': function(data) {
        $('#productModal').modal('hide');
        $('.alert-product').hide();
        $('#productModal form input').each(function() {
          $(this).val('');
        });
      }
    });
    return false;
  });

  $('#productLoteModal form').submit(function(e) {
    e.preventDefault();
    $.ajax({
      'url': $(this).attr('action'),
      'type': 'POST',
      'data': $('#productLoteModal form input').serialize(),
      'success': function(data) {
        $('#productLoteModal').modal('hide');
        $('.alert-product').hide();
        $('#productModal form input').each(function() {
          $(this).val('');
        });
      }
    });
    return false;
  });

  $.fn.modal.Constructor.prototype.enforceFocus = function() {};

})(jQuery)
