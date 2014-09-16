var intimpa = intimpa || {};

(function($) {

  $detalles = $('.detalles');
  $tplDetalle = $('#tpl-detalle-row');
  $total_venta = $('#total_venta');
  $documento = $('#documento');

  removeDetalle = function() {
    $tr = $(this).parent().parent();
    row = $tr.data('row');
    total = $tr.find('.total').text();
    $tr.remove();
    intimpa.VentaDetallesCollection.remove(row);
    previo_total = $total_venta.val() * 1;
    previo_total -= (total*1);
    $total_venta.val(previo_total.toFixed(2));
  }

  var getUnitario = function(data) {
    return (data.precio_costo / data.unidad_caja).toFixed(2);
  }

  var acProductOptions = {
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
              label: item.codigo + ' - ' + item.producto + ' ' + item.marca,
              value: item.codigo + ' - ' + item.producto + ' ' + item.marca
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
      $('#producto-id').val(ui.item.data.id);
      $('#unitario').val(getUnitario(ui.item.data));
    },
    change: function(e,ui) {
      if(!ui.item) {
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
    $descuento = $('.descuento');

    if($producto.val() !== '' &&
      $cantidad.val() !== '' &&
      $descuento.val() !== '') {
      row = $tplDetalle.html();
      template = Handlebars.compile(row);

      var row = new Date().getTime();

      data = {
        row: row,
        producto: $producto.val(),
        cantidad: $cantidad.val(),
        descuento: $descuento.val(),
        unitario: $('#unitario').val(),
        subtotal: function () {
          return (this.cantidad * this.unitario).toFixed(2);
        },
        total: function() {
          //descuento = (this.subtotal() * this.descuento) / 100;
          //return (this.subtotal() - descuento).toFixed(2);
          return (this.subtotal() - this.descuento).toFixed(2);
        }
      };

      $detalles.append(template(data));

      $detalles.find('[data-row=' + row + ']').delegate('.remove-detalle', 'click', removeDetalle);

      intimpa.VentaDetallesCollection.add({
        'row': row,
        'producto': $('#producto-id').val(),
        'precio_unitario': data.unitario,
        'cantidad': data.cantidad,
        'descuento': data.descuento,
        'total': data.total()
      }, {'validate': true});

      previo_total = $total_venta.val() * 1;
      previo_total += (data.total()*1);
      $total_venta.val(previo_total.toFixed(2));

      $producto.val('');
      $cantidad.val('').focus();
      $descuento.val(0);

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
    if(intimpa.VentaDetallesCollection.length == 0) {
      e.preventDefault();
      intimpa.betterAlert.warning('Tiene que haber al menos un detalle de la venta.');
      $cantidad.focus();
      return false;
    }
    var i = 0;
    total = 0;
    intimpa.VentaDetallesCollection.each(function(item) {
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
      objDesc = {
        'name': getName(i, 'descuento'),
        'value': item.attributes.descuento
      };
      total += parseFloat(item.attributes.total);

      tplProducto = Handlebars.compile($tplHidden.html());
      tplUnitario = Handlebars.compile($tplHidden.html());
      tplCantidad = Handlebars.compile($tplHidden.html());
      tplDescuento = Handlebars.compile($tplHidden.html());

      htmlProducto = tplProducto(objProd);
      htmlUnitario = tplUnitario(objUnit);
      htmlCantidad = tplCantidad(objCant);
      htmlDescuento = tplDescuento(objDesc);

      $form.append(htmlProducto);
      $form.append(htmlUnitario);
      $form.append(htmlCantidad);
      $form.append(htmlDescuento);
      i++;
    });

    $total_venta.val(total.toFixed(2));
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

})(jQuery)
