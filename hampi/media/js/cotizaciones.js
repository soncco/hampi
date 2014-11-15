var intimpa = intimpa || {};

(function($) {

  $detalles = $('.detalles');
  $tplDetalle = $('#tpl-detalle-row');
  $almacen = $('#almacen');
  $total_cotizacion = $('#total_cotizacion');

  removeDetalle = function() {
    $tr = $(this).parent().parent();
    row = $tr.data('row');
    total = $tr.find('.total').text();
    $tr.remove();
    intimpa.CotizacionDetallesCollection.remove(row);
    previo_total = $total_cotizacion.val() * 1;
    previo_total -= (total*1);
    $total_cotizacion.val(previo_total.toFixed(2));
  }

  var acProductOptions = {
    minLength: 1,
    source: function(request, response) {
      $.ajax({
        url: '/api/almacen/lotes-filter/',
        dataType: 'json',
        data: {
          term: request.term,
          almacen: $almacen.val()
        },
        success: function(data, e, xhr) {
          if(e)
          response($.map(data, function (item) {
            return {
              data: item,
              label: '(' + item.unidades + ') ' + item.producto.codigo + ' - ' + item.producto.producto + ' ' + item.producto.marca,
              value: item.producto.codigo + ' - ' + item.producto.producto + ' ' + item.producto.marca
            }
          }));
        }
      })
    },
    response: function(e, ui) {
      if(ui.content.length === 0) {
        var parent = $(e.target).parent();
        parent.find('.autocomplete-productos').val('');
      }
    },
    select: function(e, ui) {
      $('#producto-id').val(ui.item.data.producto.id);
      $('#unitario').val(ui.item.data.producto.precio_unidad);
    },
    change: function(e,ui) {
      if(!ui.item) {
        var parent = $(e.target).parent();
        parent.find('.autocomplete-productos').val('');
      }
    }
  }

  var acClientOptions = {
    minLength: 1,
    source: function(request, response) {
      $.ajax({
        url: '/api/clientes-filter/',
        dataType: 'json',
        data: {
          term: request.term
        },
        success: function(data, e, xhr) {
          if(e)
          response($.map(data, function (item) {
            return {
              data: item,
              label: item.numero_documento + ' - ' + item.razon_social,
              value: item.razon_social,
            }
          }));
        }
      })
    },
    response: function(e, ui) {
      if(ui.content.length === 0) {
        var parent = $(e.target).parent();
        parent.find('.autocomplete-clientes').val('');
      }
    },
    select: function(e, ui) {
      $('#cliente-id').val(ui.item.data.id);
    },
  }

  $('#add-detalle').click(function() {
    $producto = $('.autocomplete-productos');
    $cantidad = $('.cantidad');
    $precio_unitario = $('.precio_unitario');

    if($producto.val() !== '' &&
      $cantidad.val() !== '') {
      row = $tplDetalle.html();
      template = Handlebars.compile(row);

      var row = new Date().getTime();
      data = {
        row: row,
        producto: $producto.val(),
        cantidad: $cantidad.val(),
        unitario: $precio_unitario.val(),
        subtotal: function () {
          return (this.cantidad * this.unitario).toFixed(2);
        },
        total: function() {
          return this.subtotal()
        }
      };

      $detalles.append(template(data));

      $detalles.find('[data-row=' + row + ']').delegate('.remove-detalle', 'click', removeDetalle);

      intimpa.CotizacionDetallesCollection.add({
        'row': row,
        'producto': $('#producto-id').val(),
        'precio_unitario': data.unitario,
        'cantidad': data.cantidad,
        'total': data.total()
      }, {'validate': true});

      previo_total = $total_cotizacion.val() * 1;
      previo_total += (data.total()*1);
      $total_cotizacion.val(previo_total.toFixed(2));

      $producto.val('');
      $cantidad.val('').focus();
      $precio_unitario.val(0);

    } else {
      intimpa.betterAlert.warning('Completa los campos requeridos del detalle.');
      $cantidad.focus();
    }
  });

  $('.autocomplete-productos').autocomplete(acProductOptions);
  $('.autocomplete-clientes').autocomplete(acClientOptions);

  $('.autocomplete-productos').change(function() {
    if($(this).val() === '') {
      $('#producto-id').val('');
      $('#unitario').val('');
    }
  });

  $('.autocomplete-clientes').change(function() {
    if($(this).val() === '') {
      $('#cliente-id').val('');
    }
  });

  $form = $('#the-form');
  $tplHidden = $('#tpl-hidden');

  getName = function(i, what) {
    return prefix + '-' + i + '-' + what;
  }

  $form.submit(function(e) {
    if(intimpa.CotizacionDetallesCollection.length == 0) {
      e.preventDefault();
      intimpa.betterAlert.warning('Tiene que haber al menos un detalle de la cotización.');
      $cantidad.focus();
      return false;
    }
    var i = 0;
    total = 0;
    intimpa.CotizacionDetallesCollection.each(function(item) {
      objProd = {
        'name': getName(i, 'producto'),
        'value': item.attributes.producto
      };
      objUnit = {
        'name': getName(i, 'precio_unitario'),
        'value': item.attributes.precio_unitario
      };
      objCant = {
        'name': getName(i, 'cantidad'),
        'value': item.attributes.cantidad
      };
      total += parseFloat(item.attributes.total);

      tplProducto = Handlebars.compile($tplHidden.html());
      tplUnitario = Handlebars.compile($tplHidden.html());
      tplCantidad = Handlebars.compile($tplHidden.html());

      htmlProducto = tplProducto(objProd);
      htmlUnitario = tplUnitario(objUnit);
      htmlCantidad = tplCantidad(objCant);

      $form.append(htmlProducto);
      $form.append(htmlUnitario);
      $form.append(htmlCantidad);
      i++;
    });

    $total_cotizacion.val(total.toFixed(2));
    $('#id_' + prefix + '-TOTAL_FORMS').val(i);
  });

  $almacen.change(function() {
    intimpa.CotizacionDetallesCollection.reset();
    $detalles.html('');
    $total_cotizacion.val(0.0);
    $('.autocomplete-productos').val('');
  });

})(jQuery)
