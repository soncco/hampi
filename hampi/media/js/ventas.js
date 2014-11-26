var intimpa = intimpa || {};

(function($) {

  $detalles = $('.detalles');
  $tplDetalle = $('#tpl-detalle-row');
  $almacen = $('#almacen');
  $tipo_venta = $('#tipo_venta');
  $total_venta = $('#total_venta');

  removeDetalle = function() {
    $tr = $(this).parent().parent();
    row = $tr.data('row');
    total = $tr.find('.total').text();
    $tr.remove();
    intimpa.VentaDetallesCollection.remove(row);
    previo_total = $total_venta.val() * 1;
    previo_total -= (total*1);
    $total_venta.val(previo_total.toFixed(3));
  }

  var acProductOptions = {
    minLength: 1,
    source: function(request, response) {
      $.ajax({
        url: '/api/almacen/stock-filter/',
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
              label: '(' + item.unidades + ') ' 
                + item.lote.numero + ' - ' 
                + item.lote.producto.producto + ' - '
                + item.lote.producto.comercial + ' - ' 
                + item.lote.producto.marca,
              value: item.lote.numero + ' - '
                + item.lote.producto.comercial + ' - ' 
                + item.lote.producto.producto + ' - ' 
                + item.lote.producto.marca
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
      $('#producto-id').val(ui.item.data.lote.id);
      $('#numero').val(ui.item.data.lote.numero);
      $('#vencimiento').val(ui.item.data.lote.vencimiento);
      $('.iunitario').val(ui.item.data.lote.producto.precio_unidad);
      cantidad = $('.cantidad').val();
      unitario = $('.iunitario').val();
      total = (cantidad * unitario).toFixed(3)
      $('.itotal').val(total);
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
              label: item.codcliente + ' - ' + item.numero_documento + ' - ' + item.razon_social,
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
      llegada = ui.item.data.direccion + ' - '
        + ui.item.data.ciudad + ' - '
        + ui.item.data.distrito;
      $('#llegada').val(llegada)
    },
  }

  $('#add-detalle').click(function() {
    $producto = $('.autocomplete-productos');
    $cantidad = $('.cantidad');
    $iunitario = $('.iunitario');
    $itotal = $('.itotal');
    $numero = $('#numero');
    $vencimiento = $('#vencimiento');

    if($producto.val() !== '' &&
      $cantidad.val() !== '' &&
      $iunitario.val() !== '' &&
      $itotal.val() !== '') {
      row = $tplDetalle.html();
      template = Handlebars.compile(row);

      var row = new Date().getTime();

      data = {
        row: row,
        producto: $producto.val(),
        numero: $numero.val(),
        vencimiento: $vencimiento.val(),
        cantidad: $cantidad.val(),
        unitario: $('.iunitario').val(),
        total: $('.itotal').val()
      };

      $detalles.append(template(data));

      $detalles.find('[data-row=' + row + ']').delegate('.remove-detalle', 'click', removeDetalle);

      intimpa.VentaDetallesCollection.add({
        'row': row,
        'lote': $('#producto-id').val(),
        'precio_unitario': data.unitario,
        'cantidad': data.cantidad,
        'unitario': data.unitario,
        'total': data.total
      }, {'validate': true});

      previo_total = $total_venta.val() * 1;
      previo_total += (data.total*1);
      $total_venta.val(previo_total.toFixed(3));

      $producto.val('');
      $cantidad.val('').focus();
      $iunitario.val('');
      $itotal.val('');

    } else {
      intimpa.betterAlert.warning('Completa los campos requeridos del detalle.');
      $('.cantidad').focus();
    }
  });

  $('.autocomplete-productos').autocomplete(acProductOptions);
  $('.autocomplete-clientes').autocomplete(acClientOptions);

  $('.autocomplete-productos').change(function() {
    if($(this).val() === '') {
      $('#producto-id').val('');
      $('.iunitario').val('');
      $('.itotal').val('');
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
    if(intimpa.VentaDetallesCollection.length == 0) {
      e.preventDefault();
      intimpa.betterAlert.warning('Tiene que haber al menos un detalle de la venta.');
      $('.cantidad').focus();
      return false;
    }
    var i = 0;
    total = 0;
    intimpa.VentaDetallesCollection.each(function(item) {
      objProd = {
        'name': getName(i, 'lote'),
        'value': item.attributes.lote
      };
      objUnit = {
        'name': getName(i, 'precio_unitario'),
        'value': item.attributes.precio_unitario
      };
      objCant = {
        'name': getName(i, 'cantidad'),
        'value': item.attributes.cantidad
      };
      objTotal = {
        'name': getName(i, 'total'),
        'value': item.attributes.total
      };
      total += parseFloat(item.attributes.total);

      tplProducto = Handlebars.compile($tplHidden.html());
      tplUnitario = Handlebars.compile($tplHidden.html());
      tplCantidad = Handlebars.compile($tplHidden.html());
      tplTotal = Handlebars.compile($tplHidden.html());

      htmlProducto = tplProducto(objProd);
      htmlUnitario = tplUnitario(objUnit);
      htmlCantidad = tplCantidad(objCant);
      htmlTotal = tplTotal(objTotal);

      $form.append(htmlProducto);
      $form.append(htmlUnitario);
      $form.append(htmlCantidad);
      $form.append(htmlTotal);
      i++;
    });

    $total_venta.val(total.toFixed(3));

    $('#id_' + prefix + '-TOTAL_FORMS').val(i);

  });

  $almacen.change(function() {
    intimpa.VentaDetallesCollection.reset();
    $detalles.html('');
    $total_venta.val(0.0);
    $('.autocomplete-productos').val('');
  });

  $tipo_venta.change(function() {
    val = $(this).val();
    if(val == 'P') {
      $('#monto').parent().show().addClass('animated bounceIn');
      $('#monto').attr('required', 'required');
    } else {
      $('#monto').parent().hide().removeClass('animated bounceIn');
      $('#monto').removeAttr('required');
    }
  });

  $('.cantidad').change(function() {
    unitario = $('.iunitario').val();
    cantidad = $('.cantidad').val();
    total = (unitario * cantidad).toFixed(3)
    $('.itotal').val(total);
  });

  $('.iunitario').change(function() {
    unitario = $('.iunitario').val();
    cantidad = $('.cantidad').val();
    total = (unitario * cantidad).toFixed(3)
    $('.itotal').val(total);
  });

  $('.datepicker-start').datepicker({
    changeMonth: true,
    changeYear: true,
    dateFormat: 'yy-mm-dd',
    onSelect: function(date) {
      debugger;
      $end = $('.datepicker-end');
      endDate = $(this).datepicker('getDate', '+30d');
      endDate.setDate(endDate.getDate()+30);
      $end.datepicker('setDate', endDate);
    }
  });

})(jQuery)
