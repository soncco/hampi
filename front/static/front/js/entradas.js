var intimpa = intimpa || {};

(function($) {

  $detalles = $('.detalles');
  $tplDetalle = $('#tpl-detalle-row');
  $documento = $('#documento');

  removeDetalle = function() {
    $tr = $(this).parent().parent();
    row = $tr.data('row');
    total = $tr.find('.total').text();
    $tr.remove();
    intimpa.EntradaDetallesCollection.remove(row);
  }

  var acProductOptions = {
    minLength: 1,
    source: function(request, response) {
      $.ajax({
        url: '/api/lotes-filter/',
        dataType: 'json',
        data: {
          term: request.term
        },
        success: function(data, e, xhr) {
          if(e)
          response($.map(data, function (item) {
            return {
              data: item,
              label: item.numero + ' - '
                + item.producto.producto + ' - '
                + item.vencimiento + ' - '
                + item.producto.comercial + ' - '
                + item.producto.marca,
              value: item.numero + ' - '
                + item.producto.producto + ' - '
                + item.vencimiento + ' - '
                + item.producto.comercial + ' - '
                + item.producto.marca
            }
          }));
        }
      })
    },
    response: function(e, ui) {
      if(ui.content.length === 0) {
        $('.alert-product').show();
        var parent = $(e.target).parent();
        parent.find('.autocomplete-productos').val('');
      }
    },
    select: function(e, ui) {
      $('#producto-id').val(ui.item.data.id);
      $('#unitario').val(ui.item.data.producto.precio_unidad);
      $('#vencimiento').val(ui.item.data.vencimiento);
      $('#numero').val(ui.item.data.numero);
    },
    change: function(e,ui) {
      if(!ui.item) {
        $('.alert-product').show();
        var parent = $(e.target).parent();
        parent.find('.autocomplete-productos').val('');
      }
    }
  }

  var acProveedorOptions = {
    minLength: 1,
    source: function(request, response) {
      $.ajax({
        url: '/api/proveedores-filter/',
        dataType: 'json',
        data: {
          term: request.term
        },
        success: function(data, e, xhr) {
          if(e)
          response($.map(data, function (item) {
            return {
              data: item,
              label: item.razon_social,
              value: item.razon_social,
            }
          }));
        }
      })
    },
    response: function(e, ui) {
      if(ui.content.length === 0) {
        var parent = $(e.target).parent();
        parent.find('.autocomplete-proveedores').val('');
      }
    },
    select: function(e, ui) {
      $('#proveedor-id').val(ui.item.data.id);
    },
  }

  $('#add-detalle').click(function() {
    $producto = $('.autocomplete-productos');
    $cantidad = $('.cantidad');
    $vencimiento = $('#vencimiento');
    $numero = $('#numero');

    if($producto.val() !== '' &&
      $cantidad.val() !== '') {
      row = $tplDetalle.html();
      template = Handlebars.compile(row);

      var row = new Date().getTime();

      data = {
        row: row,
        vencimiento: $vencimiento.val(),
        numero: $numero.val(),
        producto: $producto.val(),
        cantidad: $cantidad.val(),
        unitario: $('#unitario').val(),
        total: function () {
          return (this.cantidad * this.unitario).toFixed(6);
        }
      };

      $detalles.append(template(data));

      $detalles.find('[data-row=' + row + ']').delegate('.remove-detalle', 'click', removeDetalle);

      intimpa.EntradaDetallesCollection.add({
        'row': row,
        'lote': $('#producto-id').val(),
        'precio_unidad': data.unitario,
        'cantidad': data.cantidad,
        'total': data.total()
      }, {'validate': true});

      $producto.val('');
      $cantidad.val('').focus();

    } else {
      intimpa.betterAlert.warning('Completa los campos requeridos del detalle.');
      $cantidad.focus();
    }
  });

  $('.autocomplete-productos').autocomplete(acProductOptions);
  $('.autocomplete-proveedores').autocomplete(acProveedorOptions);

  $('.autocomplete-productos').change(function() {
    if($(this).val() === '') {
      $('#producto-id').val('');
      $('#unitario').val('');
    }
  });

  $('.autocomplete-proveedores').change(function() {
    if($(this).val() === '') {
      $('#proveedor-id').val('');
    }
  });

  $form = $('#the-form');
  $tplHidden = $('#tpl-hidden');

  getName = function(i, what) {
    return prefix + '-' + i + '-' + what;
  }

  $form.submit(function(e) {
    if(intimpa.EntradaDetallesCollection.length == 0) {
      e.preventDefault();
      intimpa.betterAlert.warning('Tiene que haber al menos un detalle de la venta.');
      $cantidad.focus();
      return false;
    }
    var i = 0;
    total = 0;
    intimpa.EntradaDetallesCollection.each(function(item) {
      objProd = {
        'name': getName(i, 'lote'),
        'value': item.attributes.lote
      };
      objUnit = {
        'name': getName(i, 'precio_unitario'),
        'value': item.attributes.precio_unidad
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

    $('#id_' + prefix + '-TOTAL_FORMS').val(i);
    //e.preventDefault();
    //return false;
  });

  $documento.change(function() {
    val = $(this).val();
    if(val != 'G') {
      $('#proveedor').parent().show().addClass('animated bounceIn');
      $('#proveedor').attr('required', 'required');
    } else {
      $('#proveedor').parent().hide().removeClass('animated bounceIn');
      $('#proveedor').removeAttr('required');
    }
  });

  $('.alert-product').hide();

})(jQuery)
