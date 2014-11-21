# -*- coding: utf-8 -*-

from models import Stock, Salida, SalidaDetalle

def salida_stock(salida):
  detalles = salida.salidadetalle_set.all()
  for detalle in detalles:
    quitar_stock(detalle, salida.almacen)

def entrada_stock(entrada):
  detalles = entrada.entradadetalle_set.all()
  for detalle in detalles:
    agregar_stock(detalle, entrada.almacen)

def existe_stock(lote, en_almacen):
  conteo = Stock.objects.filter(lote = lote, en_almacen = en_almacen).count()
  return (conteo > 0)

def quitar_stock(detalle, almacen):
  stock = Stock.objects.get(lote = detalle.lote, en_almacen = almacen)
  stock.unidades = stock.unidades - detalle.cantidad
  stock.save()

def agregar_stock(detalle, almacen):
  if existe_stock(detalle.lote, almacen):
    stock = Stock.objects.get(lote = detalle.lote, en_almacen = almacen)
    stock.unidades = stock.unidades + detalle.cantidad
    stock.save()
  else:
    stock = Stock(lote = detalle.lote, en_almacen = almacen, unidades = detalle.cantidad)
    stock.save()

def generar_salida_venta(venta):
  salida = Salida()
  salida.fecha = venta.fecha_factura
  salida.numero_factura = venta.numero_factura
  salida.fecha_factura = venta.fecha_factura
  salida.numero_guia = venta.numero_guia
  salida.fecha_guia = venta.fecha_guia
  salida.almacen = venta.almacen
  salida.notas = 'Salida generada desde la Venta número %s' % venta.pk
  salida.quien = venta.vendedor
  salida.venta = venta
  salida.save()

  for detalle in venta.ventadetalle_set.all():
    salida_detalle = SalidaDetalle()
    salida_detalle.lote = detalle.lote
    salida_detalle.precio_unitario = detalle.precio_unitario
    salida_detalle.cantidad = detalle.cantidad
    salida_detalle.total = detalle.total
    salida_detalle.salida_padre = salida
    salida_detalle.save()

  return salida

def total_monto_stock(en_almacen):
  stock = Stock.objects.filter(en_almacen = en_almacen)
  total = 0
  for row in stock:
    total += row.unidades * row.lote.producto.precio_unidad
  return total

def total_monto_stock_real(en_almacen):
  stock = Stock.objects.filter(en_almacen = en_almacen)
  total = 0
  for row in stock:
    total += row.unidades * row.lote.producto.precio_unidad
  return total
