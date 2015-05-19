# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from xlsxwriter.workbook import Workbook
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

from datetime import date
import datetime

from ventas.models import Deuda, Venta, VentaDetalle, Cotizacion, CotizacionDetalle
from ventas.utils import total_amortizaciones, saldo_deuda

from almacen.models import Entrada, EntradaDetalle, Salida, SalidaDetalle, Stock, Almacen

from core.models import Producto, Gasto, Cliente, Proveedor

from front.utils import diff_dates

@login_required
def excel_deudas(request):

  inicio = request.POST.get('inicio')
  fin = request.POST.get('fin')
  tipo = request.POST.get('tipo')

  deudas = Deuda.objects.filter(registro_padre__fecha_factura__range = (inicio, fin)).order_by('id')

  if tipo != 'todos':
    if tipo == 'cancelados':
      deudas = deudas.filter(estado = 'C')
    else:
      deudas = deudas.filter(estado = 'D')


  output = StringIO.StringIO()

  book = Workbook(output)  
  sheet = book.add_worksheet(u'Créditos')

  bold = book.add_format({'bold': 1})
  fecha = book.add_format({'num_format': 'dd/mm/yy'})
  money = book.add_format({'num_format': '0.00'})

  title = book.add_format({
    'bold': 1,
    'align': 'center',
    'font_color': 'white',
    'fg_color': '#18bc9c',
  })

  fecha2 = book.add_format({
    'bold': 1,
    'align': 'center',
    'font_color': 'white',
    'fg_color': '#2ecc71',
    'num_format': 'd mmm yyyy'
  })

  sheet.merge_range('A1:J1', u'Reporte de Créditos', title)
  sheet.write('K1', u'Fecha Inicio:', bold)
  sheet.write('L1', datetime.datetime.strptime(inicio, "%Y-%m-%d"), fecha2)
  sheet.write('M1', u'Fecha Fin:', bold)
  sheet.write('N1', datetime.datetime.strptime(fin, "%Y-%m-%d"), fecha2)

  sheet.write('A3', u'Almacén', bold)
  sheet.write('B3', u'Fecha', bold)
  sheet.write('C3', u'Documento', bold)
  sheet.write('D3', u'Total Venta', bold)
  sheet.write('E3', u'Total Amortización', bold)
  sheet.write('F3', u'Saldo', bold)
  sheet.write('G3', u'Cliente', bold)
  sheet.write('H3', u'Segmento', bold)
  sheet.write('I3', u'Ciudad', bold)
  sheet.write('J3', u'Distrito', bold)
  sheet.write('K3', u'Días de deuda', bold)
  sheet.write('L3', u'Número de Venta', bold)
  sheet.write('M3', u'Vendedor', bold)
  sheet.write('N3', u'Estado', bold)

  row = 4
  for deuda in deudas:
    sheet.write('A%s' % row, deuda.registro_padre.almacen.nombre)
    sheet.write('B%s' % row, deuda.registro_padre.fecha_factura, fecha)
    sheet.write('C%s' % row, deuda.registro_padre.numero_factura)
    sheet.write('D%s' % row, deuda.total, money)
    sheet.write('E%s' % row, total_amortizaciones(deuda), money)
    sheet.write_formula('F%s' % row, '{=D%s-E%s}' % (row, row), money)
    sheet.write('G%s' % row, deuda.registro_padre.cliente.razon_social)
    sheet.write('H%s' % row, deuda.registro_padre.cliente.segmento.nombre)
    sheet.write('I%s' % row, deuda.registro_padre.cliente.ciudad)
    sheet.write('J%s' % row, deuda.registro_padre.cliente.distrito)
    sheet.write('K%s' % row, diff_dates(deuda.registro_padre.fecha_factura, date.today()))
    sheet.write('L%s' % row, deuda.registro_padre.pk)
    sheet.write('M%s' % row, deuda.registro_padre.vendedor.username)
    sheet.write('N%s' % row, deuda.get_estado_display())
    row += 1

  sheet.autofilter(('A3:N%s' % row))
  book.close()

  # construct response
  output.seek(0)
  response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
  response['Content-Disposition'] = "attachment; filename=creditos-%s.xlsx" % date.today()

  return response

@login_required
def excel_ventas(request):

  inicio = request.POST.get('inicio')
  fin = request.POST.get('fin')

  ventas = VentaDetalle.objects.filter(registro_padre__fecha_factura__range = (inicio, fin)).order_by('id')

  output = StringIO.StringIO()

  book = Workbook(output)  
  sheet = book.add_worksheet(u'Ventas')

  bold = book.add_format({'bold': 1})
  fecha = book.add_format({'num_format': 'dd/mm/yy'})
  money = book.add_format({'num_format': '0.00'})

  title = book.add_format({
    'bold': 1,
    'align': 'center',
    'font_color': 'white',
    'fg_color': '#18bc9c',
  })

  fecha2 = book.add_format({
    'bold': 1,
    'align': 'center',
    'font_color': 'white',
    'fg_color': '#2ecc71',
    'num_format': 'd mmm yyyy'
  })

  sheet.merge_range('A1:O1', u'Reporte de Ventas', title)
  sheet.write('P1', u'Fecha Inicio:', bold)
  sheet.write('Q1', datetime.datetime.strptime(inicio, "%Y-%m-%d"), fecha2)
  sheet.write('R1', u'Fecha Fin:', bold)
  sheet.write('S1', datetime.datetime.strptime(fin, "%Y-%m-%d"), fecha2)

  sheet.write('A3', u'Número', bold)
  sheet.write('B3', u'Cliente', bold)
  sheet.write('C3', u'Segmento', bold)
  sheet.write('D3', u'Ciudad', bold)
  sheet.write('E3', u'Distrito', bold)
  sheet.write('F3', u'Código de Producto', bold)
  sheet.write('G3', u'Producto', bold)
  sheet.write('H3', u'Lote', bold)
  sheet.write('I3', u'Vencimiento', bold)
  sheet.write('J3', u'Precio Unitario', bold)
  sheet.write('K3', u'Cantidad', bold)
  sheet.write('L3', u'Total', bold)
  sheet.write('M3', u'Fecha de Venta', bold)
  sheet.write('N3', u'Número de Documento', bold)
  sheet.write('O3', u'Vendedor', bold)
  sheet.write('P3', u'Total Venta', bold)
  sheet.write('Q3', u'Total Amortización', bold)
  sheet.write('R3', u'Saldo', bold)
  sheet.write('S3', u'Tipo', bold)
  sheet.write('T3', u'Almacén', bold)

  row = 4
  for venta in ventas:

    sheet.write('A%s' % row, venta.registro_padre.pk)
    sheet.write('B%s' % row, venta.registro_padre.cliente.razon_social)
    sheet.write('C%s' % row, venta.registro_padre.cliente.segmento.nombre)
    sheet.write('D%s' % row, venta.registro_padre.cliente.ciudad)
    sheet.write('E%s' % row, venta.registro_padre.cliente.distrito)
    sheet.write('F%s' % row, venta.lote.producto.codigo)
    sheet.write('G%s' % row, venta.lote.producto.producto)
    sheet.write('H%s' % row, venta.lote.numero)
    sheet.write('I%s' % row, venta.lote.vencimiento, fecha)
    sheet.write('J%s' % row, venta.precio_unitario, money)
    sheet.write('K%s' % row, venta.cantidad)
    sheet.write_formula('L%s' % row, '{=K%s*J%s}' % (row, row))
    sheet.write('M%s' % row, venta.registro_padre.fecha_factura, fecha)
    sheet.write('N%s' % row, venta.registro_padre.numero_factura)
    sheet.write('O%s' % row, venta.registro_padre.vendedor.username)
    sheet.write('P%s' % row, venta.registro_padre.total_venta)
    try:
      sheet.write('Q%s' % row, total_amortizaciones(venta.registro_padre.deuda))
    except:
      sheet.write('Q%s' % row, 'Contado')

    try:
      sheet.write('R%s' % row, saldo_deuda(venta.registro_padre.deuda))
      sheet.write_formula('Q%s' % row, '{=P%s-Q%s}' % (row, row), money)
    except:
      sheet.write('R%s' % row, 'Sin saldo')

    sheet.write('S%s' % row, venta.registro_padre.get_tipo_venta_display())
    sheet.write('T%s' % row, venta.registro_padre.almacen.nombre)
    row += 1

  sheet.autofilter(('A3:T%s' % row))
  book.close()

  # construct response
  output.seek(0)
  response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
  response['Content-Disposition'] = "attachment; filename=ventas-%s.xlsx" % date.today()

  return response

from django.db.models.aggregates import Sum
@login_required
def excel_ranking(request):

  inicio = request.POST.get('inicio')
  fin = request.POST.get('fin')

  ventas = VentaDetalle.objects.filter(registro_padre__fecha_factura__range = (inicio, fin)).order_by('id')

  productos = Producto.objects.filter(activo = True)

  output = StringIO.StringIO()

  book = Workbook(output)  
  sheet = book.add_worksheet(u'Ranking')

  bold = book.add_format({'bold': 1})

  title = book.add_format({
    'bold': 1,
    'align': 'center',
    'font_color': 'white',
    'fg_color': '#18bc9c',
  })

  fecha2 = book.add_format({
    'bold': 1,
    'align': 'center',
    'font_color': 'white',
    'fg_color': '#2ecc71',
    'num_format': 'd mmm yyyy'
  })

  sheet.merge_range('A1:C1', u'Ranking de Productos', title)

  sheet.write('D1', u'Fecha Inicio:', bold)
  sheet.write('E1', datetime.datetime.strptime(inicio, "%Y-%m-%d"), fecha2)
  sheet.write('F1', u'Fecha Fin:', bold)
  sheet.write('G1', datetime.datetime.strptime(fin, "%Y-%m-%d"), fecha2)

  sheet.write('A3', u'Producto', bold)
  sheet.write('B3', u'Cantidad Vendida', bold)

  row = 4
  for producto in productos:
    p = ventas.filter(lote__producto = producto)
    suma = p.aggregate(Sum('cantidad'))
    if suma['cantidad__sum'] != None:
      sheet.write('A%s' % row, producto.producto)
      sheet.write('B%s' % row, producto.codigo)
      sheet.write('C%s' % row, suma['cantidad__sum'])
      row += 1

  sheet.autofilter(('A3:C%s' % row))

  chart = book.add_chart({'type': 'pie'})

  chart.add_series({
    'name': 'Ranking',
    'categories': '=Ranking!B4:B%s' % row,
    'values':     '=Ranking!C4:C%s' % row,
  })

  chart.set_title({'name': 'Ranking de Productos'})

  sheet.insert_chart('D2', chart)
  

  sheet.write('A%s' % str(row+1), 'Los productos que no se vendieron no aparecen.')

  book.close()

  # construct response
  output.seek(0)
  response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
  response['Content-Disposition'] = "attachment; filename=ranking-%s.xlsx" % date.today()

  return response

@login_required
def excel_entradas(request):

  inicio = request.POST.get('inicio')
  fin = request.POST.get('fin')

  entradas = EntradaDetalle.objects.filter(entrada_padre__fecha_factura__range = (inicio, fin)).order_by('id')

  output = StringIO.StringIO()

  book = Workbook(output)  
  sheet = book.add_worksheet(u'Entradas')

  bold = book.add_format({'bold': 1})
  fecha = book.add_format({'num_format': 'dd/mm/yy'})
  money = book.add_format({'num_format': '0.00'})

  title = book.add_format({
    'bold': 1,
    'align': 'center',
    'font_color': 'white',
    'fg_color': '#18bc9c',
  })

  fecha2 = book.add_format({
    'bold': 1,
    'align': 'center',
    'font_color': 'white',
    'fg_color': '#2ecc71',
    'num_format': 'd mmm yyyy'
  })

  sheet.merge_range('A1:F1', u'Reporte de Entradas', title)
  sheet.write('G1', u'Fecha Inicio:', bold)
  sheet.write('H1', datetime.datetime.strptime(inicio, "%Y-%m-%d"), fecha2)
  sheet.write('I1', u'Fecha Fin:', bold)
  sheet.write('J1', datetime.datetime.strptime(fin, "%Y-%m-%d"), fecha2)

  sheet.write('A3', u'Fecha', bold)
  sheet.write('B3', u'Número de Factura', bold)
  sheet.write('C3', u'Fecha de Guía', bold)
  sheet.write('D3', u'Almacén', bold)
  sheet.write('E3', u'Proveedor', bold)
  sheet.write('F3', u'Quién', bold)
  sheet.write('G3', u'Código', bold)
  sheet.write('H3', u'Producto', bold)
  sheet.write('I3', u'Cantidad', bold)
  sheet.write('J3', u'Lote', bold)
  sheet.write('K3', u'Vencimiento', bold)

  row = 4
  for entrada in entradas:

    sheet.write('A%s' % row, entrada.entrada_padre.fecha, fecha)
    sheet.write('B%s' % row, entrada.entrada_padre.numero_factura)
    sheet.write('C%s' % row, entrada.entrada_padre.fecha_factura, fecha)
    sheet.write('D%s' % row, entrada.entrada_padre.almacen.nombre)
    try:
      sheet.write('E%s' % row, entrada.entrada_padre.proveedor.razon_social)
    except:
      sheet.write('E%s' % row, 'Sin Proveedor')
    sheet.write('F%s' % row, entrada.entrada_padre.quien.username)
    sheet.write('G%s' % row, entrada.lote.producto.codigo)
    sheet.write('H%s' % row, entrada.lote.producto.producto)
    sheet.write('I%s' % row, entrada.cantidad)
    sheet.write('J%s' % row, entrada.lote.numero)
    sheet.write('K%s' % row, entrada.lote.vencimiento, fecha)

    row += 1

  sheet.autofilter(('A3:K%s' % row))
  book.close()

  # construct response
  output.seek(0)
  response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
  response['Content-Disposition'] = "attachment; filename=entradas-%s.xlsx" % date.today()

  return response

@login_required
def excel_salidas(request):

  inicio = request.POST.get('inicio')
  fin = request.POST.get('fin')

  salidas = SalidaDetalle.objects.filter(salida_padre__fecha_documento__range = (inicio, fin)).order_by('id')

  output = StringIO.StringIO()

  book = Workbook(output)  
  sheet = book.add_worksheet(u'Salidas')

  bold = book.add_format({'bold': 1})
  fecha = book.add_format({'num_format': 'dd/mm/yy'})
  money = book.add_format({'num_format': '0.00'})

  title = book.add_format({
    'bold': 1,
    'align': 'center',
    'font_color': 'white',
    'fg_color': '#18bc9c',
  })

  fecha2 = book.add_format({
    'bold': 1,
    'align': 'center',
    'font_color': 'white',
    'fg_color': '#2ecc71',
    'num_format': 'd mmm yyyy'
  })

  sheet.merge_range('A1:F1', u'Reporte de Entradas', title)
  sheet.write('G1', u'Fecha Inicio:', bold)
  sheet.write('H1', datetime.datetime.strptime(inicio, "%Y-%m-%d"), fecha2)
  sheet.write('I1', u'Fecha Fin:', bold)
  sheet.write('J1', datetime.datetime.strptime(fin, "%Y-%m-%d"), fecha2)

  sheet.write('A3', u'Fecha', bold)
  sheet.write('B3', u'Documento', bold)
  sheet.write('C3', u'Número de Documento', bold)
  sheet.write('D3', u'Fecha de Documento', bold)
  sheet.write('E3', u'Almacén', bold)
  sheet.write('F3', u'Venta Relacionada', bold)
  sheet.write('G3', u'Quién', bold)
  sheet.write('H3', u'Código', bold)
  sheet.write('I3', u'Producto', bold)
  sheet.write('J3', u'Cantidad', bold)
  sheet.write('K3', u'Lote', bold)
  sheet.write('L3', u'Vencimiento', bold)

  row = 4
  for salida in salidas:

    sheet.write('A%s' % row, salida.salida_padre.fecha, fecha)
    sheet.write('B%s' % row, salida.salida_padre.get_documento_display())
    sheet.write('C%s' % row, salida.salida_padre.numero_documento)
    sheet.write('D%s' % row, salida.salida_padre.fecha_documento, fecha)
    sheet.write('E%s' % row, salida.salida_padre.almacen.nombre)
    sheet.write('F%s' % row, salida.salida_padre.venta.pk if salida.salida_padre.venta != None else 'Sin venta')
    sheet.write('G%s' % row, salida.salida_padre.quien.username)
    sheet.write('H%s' % row, salida.lote.producto.codigo)
    sheet.write('I%s' % row, salida.lote.producto.producto)
    sheet.write('J%s' % row, salida.cantidad)
    sheet.write('K%s' % row, salida.lote.numero)
    sheet.write('L%s' % row, salida.lote.vencimiento, fecha)

    row += 1

  sheet.autofilter(('A3:L%s' % row))
  book.close()

  # construct response
  output.seek(0)
  response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
  response['Content-Disposition'] = "attachment; filename=salidas-%s.xlsx" % date.today()

  return response

@login_required
def excel_gastos(request):

  inicio = request.POST.get('inicio')
  fin = request.POST.get('fin')

  gastos = Gasto.objects.filter(fecha__range = (inicio, fin))

  output = StringIO.StringIO()

  book = Workbook(output)  
  sheet = book.add_worksheet(u'Gastos')

  bold = book.add_format({'bold': 1})
  fecha = book.add_format({'num_format': 'dd/mm/yy'})
  money = book.add_format({'num_format': '0.00'})

  title = book.add_format({
    'bold': 1,
    'align': 'center',
    'font_color': 'white',
    'fg_color': '#18bc9c',
  })

  fecha2 = book.add_format({
    'bold': 1,
    'align': 'center',
    'font_color': 'white',
    'fg_color': '#2ecc71',
    'num_format': 'd mmm yyyy'
  })

  sheet.merge_range('A1:B1', u'Reporte de Gastos', title)
  sheet.write('C1', u'Fecha Inicio:', bold)
  sheet.write('D1', datetime.datetime.strptime(inicio, "%Y-%m-%d"), fecha2)
  sheet.write('E1', u'Fecha Fin:', bold)
  sheet.write('F1', datetime.datetime.strptime(fin, "%Y-%m-%d"), fecha2)

  sheet.write('A3', u'Fecha', bold)
  sheet.write('B3', u'Quién', bold)
  sheet.write('C3', u'Almacén', bold)
  sheet.write('D3', u'Tipo de Gasto', bold)
  sheet.write('E3', u'Monto', bold)
  sheet.write('F3', u'Razón', bold)

  row = 4
  for gasto in gastos:

    sheet.write('A%s' % row, gasto.fecha, fecha)
    sheet.write('B%s' % row, gasto.quien.username)
    sheet.write('C%s' % row, gasto.almacen.nombre)
    try:
      sheet.write('D%s' % row, gasto.tipo.nombre)
    except:
      sheet.write('D%s' % row, 'Ninguno')
    sheet.write('E%s' % row, gasto.monto, money)
    sheet.write('F%s' % row, gasto.razon)

    row += 1

  sheet.autofilter(('A3:F%s' % row))
  book.close()

  # construct response
  output.seek(0)
  response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
  response['Content-Disposition'] = "attachment; filename=gastos-%s.xlsx" % date.today()

  return response


@login_required
def excel_inventario(request):
  almacen = request.POST.get('almacen')

  if almacen == '0':
    stock = Stock.objects.all()
  else:
    the_almacen = Almacen.objects.get(pk = almacen)
    stock = Stock.objects.filter(en_almacen = the_almacen)

  output = StringIO.StringIO()

  book = Workbook(output)  
  sheet = book.add_worksheet(u'Inventario')

  bold = book.add_format({'bold': 1})
  money = book.add_format({'num_format': '0.00'})

  title = book.add_format({
    'bold': 1,
    'align': 'center',
    'font_color': 'white',
    'fg_color': '#18bc9c',
  })

  sheet.merge_range('A1:H1', u'Inventario', title)

  sheet.write('A3', u'Código', bold)
  sheet.write('B3', u'Producto', bold)
  sheet.write('C3', u'Lote', bold)
  sheet.write('D3', u'Vencimiento', bold)
  sheet.write('E3', u'Cantidad', bold)
  sheet.write('F3', u'Unitario', bold)
  sheet.write('G3', u'Precio Crédito', bold)
  sheet.write('H3', u'Total Venta', bold)
  sheet.write('I3', u'Total Real', bold)
  sheet.write('J3', u'Almacén', bold)

  row = 4
  for st in stock:

    sheet.write('A%s' % row, st.lote.producto.codigo)
    sheet.write('B%s' % row, st.lote.producto.producto)
    sheet.write('C%s' % row, st.lote.numero)
    sheet.write('D%s' % row, st.lote.fecha)
    sheet.write('E%s' % row, st.unidades)
    sheet.write('F%s' % row, st.producto.precio_unidad, money)
    sheet.write('G%s' % row, (st.producto.precio_credito / st.producto.unidad_caja), money)
    sheet.write_formula('H%s' % row, '{=E%s*F%s}' % (row, row))
    sheet.write_formula('I%s' % row, '{=E%s*G%s}' % (row, row))
    sheet.write('J%s' % row, st.en_almacen.nombre)

    row += 1

  sheet.autofilter(('A3:J%s' % row))
  book.close()

  # construct response
  output.seek(0)
  response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
  response['Content-Disposition'] = "attachment; filename=inventario-%s.xlsx" % date.today()

  return response

@login_required
def excel_clientes(request):

  clientes = Cliente.objects.all()

  output = StringIO.StringIO()

  book = Workbook(output)  
  sheet = book.add_worksheet(u'Clientes')

  bold = book.add_format({'bold': 1})

  title = book.add_format({
    'bold': 1,
    'align': 'center',
    'font_color': 'white',
    'fg_color': '#18bc9c',
  })

  sheet.merge_range('A1:H1', u'Relación de Clientes', title)

  sheet.write('A3', u'Razón Social', bold)
  sheet.write('B3', u'Segmento', bold)
  sheet.write('C3', u'Tipo de Documento', bold)
  sheet.write('D3', u'Número de Documento', bold)
  sheet.write('E3', u'Dirección', bold)
  sheet.write('F3', u'Teléfono', bold)
  sheet.write('G3', u'Ciudad', bold)
  sheet.write('H3', u'Distrito', bold)

  row = 4
  for cliente in clientes:

    sheet.write('A%s' % row, cliente.razon_social)
    sheet.write('B%s' % row, cliente.segmento.nombre)
    sheet.write('C%s' % row, cliente.get_tipo_documento_display())
    sheet.write('D%s' % row, cliente.numero_documento)
    sheet.write('E%s' % row, cliente.direccion)
    sheet.write('F%s' % row, cliente.telefono)
    sheet.write('G%s' % row, cliente.ciudad)
    sheet.write('H%s' % row, cliente.distrito)

    row += 1

  sheet.autofilter(('A3:H%s' % row))
  book.close()

  # construct response
  output.seek(0)
  response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
  response['Content-Disposition'] = "attachment; filename=clientes-%s.xlsx" % date.today()

  return response

@login_required
def excel_proveedores(request):

  proveedores = Proveedor.objects.all()

  output = StringIO.StringIO()

  book = Workbook(output)  
  sheet = book.add_worksheet(u'Proveedores')

  bold = book.add_format({'bold': 1})

  title = book.add_format({
    'bold': 1,
    'align': 'center',
    'font_color': 'white',
    'fg_color': '#18bc9c',
  })

  sheet.merge_range('A1:F1', u'Relación de Proveedores', title)

  sheet.write('A3', u'Razón Social', bold)
  sheet.write('B3', u'RUC', bold)
  sheet.write('C3', u'Dirección', bold)
  sheet.write('D3', u'Teléfono', bold)
  sheet.write('E3', u'Ciudad', bold)
  sheet.write('F3', u'Distrito', bold)

  row = 4
  for proveedor in proveedores:

    sheet.write('A%s' % row, proveedor.razon_social)
    sheet.write('B%s' % row, proveedor.ruc)
    sheet.write('C%s' % row, proveedor.direccion)
    sheet.write('D%s' % row, proveedor.telefono)
    sheet.write('E%s' % row, proveedor.ciudad)
    sheet.write('F%s' % row, proveedor.distrito)

    row += 1

  sheet.autofilter(('A3:F%s' % row))
  book.close()

  # construct response
  output.seek(0)
  response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
  response['Content-Disposition'] = "attachment; filename=proveedores-%s.xlsx" % date.today()

  return response

@login_required
def excel_cotizaciones(request):

  inicio = request.POST.get('inicio')
  fin = request.POST.get('fin')

  cotizaciones = CotizacionDetalle.objects.filter(registro_padre__fecha__range = (inicio, fin)).order_by('id')

  output = StringIO.StringIO()

  book = Workbook(output)  
  sheet = book.add_worksheet(u'Cotizaciones')

  bold = book.add_format({'bold': 1})
  fecha = book.add_format({'num_format': 'dd/mm/yy'})
  money = book.add_format({'num_format': '0.00'})

  title = book.add_format({
    'bold': 1,
    'align': 'center',
    'font_color': 'white',
    'fg_color': '#18bc9c',
  })

  fecha2 = book.add_format({
    'bold': 1,
    'align': 'center',
    'font_color': 'white',
    'fg_color': '#2ecc71',
    'num_format': 'd mmm yyyy'
  })

  sheet.merge_range('A1:I1', u'Reporte de Cotizaciones', title)
  sheet.write('J1', u'Fecha Inicio:', bold)
  sheet.write('K1', datetime.datetime.strptime(inicio, "%Y-%m-%d"), fecha2)
  sheet.write('L1', u'Fecha Fin:', bold)
  sheet.write('M1', datetime.datetime.strptime(fin, "%Y-%m-%d"), fecha2)

  sheet.write('A3', u'Número', bold)
  sheet.write('B3', u'Cliente', bold)
  sheet.write('C3', u'Segmento', bold)
  sheet.write('D3', u'Ciudad', bold)
  sheet.write('E3', u'Código de Producto', bold)
  sheet.write('F3', u'Producto', bold)
  sheet.write('G3', u'Marca', bold)
  sheet.write('H3', u'Precio Unitario', bold)
  sheet.write('I3', u'Cantidad', bold)
  sheet.write('J3', u'Valor', bold)
  sheet.write('K3', u'Fecha', bold)
  sheet.write('L3', u'Quien', bold)
  sheet.write('M3', u'Total Cotización', bold)

  row = 4
  for cotizacion in cotizaciones:

    sheet.write('A%s' % row, cotizacion.registro_padre.pk)
    sheet.write('B%s' % row, cotizacion.registro_padre.cliente.razon_social)
    sheet.write('C%s' % row, cotizacion.registro_padre.cliente.segmento.nombre)
    sheet.write('D%s' % row, cotizacion.registro_padre.cliente.ciudad)
    sheet.write('E%s' % row, cotizacion.producto.codigo)
    sheet.write('F%s' % row, cotizacion.producto.producto)
    sheet.write('G%s' % row, cotizacion.producto.marca)
    sheet.write('H%s' % row, cotizacion.precio_unitario, money)
    sheet.write('I%s' % row, cotizacion.cantidad)
    sheet.write_formula('J%s' % row, '{=H%s*I%s}' % (row, row))
    sheet.write('K%s' % row, cotizacion.registro_padre.fecha, fecha)
    sheet.write('L%s' % row, cotizacion.registro_padre.quien.username)
    sheet.write('M%s' % row, cotizacion.registro_padre.total_cotizacion)
    row += 1

  sheet.autofilter(('A3:M%s' % row))
  book.close()

  # construct response
  output.seek(0)
  response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
  response['Content-Disposition'] = "attachment; filename=cotizaciones-%s.xlsx" % date.today()

  return response

@login_required
def anexo_print(request, id):
  entrada = Entrada.objects.get(pk = id)

  output = StringIO.StringIO()

  book = Workbook(output)  
  
  bold = book.add_format({'bold': 1})
  fecha = book.add_format({'num_format': 'dd/mm/yy'})

  title = book.add_format({
    'bold': 1,
    'align': 'center',
  })

  fecha = book.add_format({
    'num_format': 'd mmm yyyy',
    'border': 1
  })

  borde = book.add_format({
    'border': 1
  })

  cabecera = book.add_format({
    'border': 1,
    'bold': 1
  })

  border_top = book.add_format({
    'top': 1,
  })

  # Anexo A

  sheet = book.add_worksheet(u'Anexo A')
  sheet.write('A3', 'Elaborado por:')
  sheet.merge_range('A5:G5', u'Anexo Nro -A', title)
  sheet.merge_range('A7:G7', u'Droguería Hampi Kallpa E.I.R.L.', title)
  sheet.merge_range('A9:G9', u'Acta de Recepción y Conformidad', title)

  sheet.write('A11', u'Fecha:', bold)
  sheet.write('F11', u'Hora:', bold)
  sheet.write('A12', u'Q.F. Director Técnico:', bold)
  sheet.write('A13', u'Proveedor:', bold)
  sheet.write('B13', entrada.proveedor.razon_social, bold)
  sheet.write('A14', u'Factura Nro:', bold)
  sheet.write('F14', u'Fecha Factura:', bold)
  sheet.write('A14', u'Guía de Remisión Nro:', bold)
  sheet.write('F14', u'Fecha G/R:', bold)

  #sheet.write('M1', datetime.datetime.strptime(fin, "%Y-%m-%d"), fecha2)

  sheet.write('A17', u'Cantidad', cabecera)
  sheet.write('B17', u'F.F.', cabecera)
  sheet.write('C17', u'Descripción', cabecera)
  sheet.write('D17', u'Fabricante', cabecera)
  sheet.write('E17', u'F/V', cabecera)
  sheet.write('F17', u'Lote', cabecera)

  row = 18
  for detalle in entrada.entradadetalle_set.all():

    sheet.write('A%s' % row, detalle.cantidad, borde)
    sheet.write('B%s' % row, detalle.lote.producto.unidad_medida, borde)
    sheet.write('C%s' % row, detalle.lote.producto.producto, borde)
    sheet.write('D%s' % row, detalle.lote.producto.marca, borde)
    sheet.write('E%s' % row, detalle.lote.vencimiento, fecha)
    sheet.write('F%s' % row, detalle.lote.numero, borde)
    row += 1

  row += 3
  sheet.write('A%s' % row, u'Q.F. Director Técnico', border_top)

  row += 2
  sheet.write('A%s' % row, u'Elaborado por', cabecera)
  sheet.write('B%s' % row, u'Revisado y Aprobado por:', cabecera)

  row += 1
  sheet.write('A%s' % row, '', borde)
  sheet.write('B%s' % row, '', borde)


  # Anexo B

  sheet = book.add_worksheet(u'Anexo B')
  sheet.write('A3', 'Elaborado por:')
  sheet.merge_range('A5:M5', u'Anexo Nro -B', title)
  sheet.merge_range('A7:M7', u'Acta de Recepción y Evaluación Organoléptica para el ingreso de productos farmaceuticos y afines al almacén de la', title)
  sheet.merge_range('A9:M9', u'Droguería Hampi Kallpa E.I.R.L.', title)

  sheet.write('A11', u'Fecha:', bold)
  sheet.write('A13', u'Nro. Factura:', bold)
  sheet.write('D13', u'Guía de Remisión:', bold)
  sheet.write('G13', u'Proveedor:', bold)
  sheet.write('H13', entrada.proveedor.razon_social, bold)

  sheet.write('A15', '', cabecera)
  sheet.merge_range('A15:D15', u'Producto', cabecera)
  sheet.merge_range('E15:F15', u'Documentos', cabecera)
  sheet.merge_range('G15:H15', u'Embalaje Adecuado', cabecera)
  sheet.merge_range('I15:J15', u'Envaso Inmediato Adecuado', cabecera)
  sheet.merge_range('K15:M15', u'Contenido', cabecera)

  sheet.write('A16', u'Nro', cabecera)
  sheet.write('B16', u'Descripción', cabecera)
  sheet.write('C16', u'Lote', cabecera)
  sheet.write('D16', u'FV', cabecera)
  sheet.write('E16', u'RS', cabecera)
  sheet.write('F16', u'Protocolo Análisis', cabecera)
  sheet.write('G16', u'Si', cabecera)
  sheet.write('H16', u'No', cabecera)
  sheet.write('I16', u'Si', cabecera)
  sheet.write('J16', u'No', cabecera)
  sheet.write('K16', u'Color', cabecera)
  sheet.write('L16', u'Aspecto', cabecera)
  sheet.write('M16', u'No cuerpos extraños', cabecera)

  row = 17
  counter = 1
  for detalle in entrada.entradadetalle_set.all():
    sheet.write('A%s' % row, counter, borde)
    sheet.write('B%s' % row, detalle.lote.producto.producto, borde)
    sheet.write('C%s' % row, detalle.lote.numero, borde)
    sheet.write('D%s' % row, detalle.lote.vencimiento, fecha)
    sheet.write('E%s' % row, '', borde)
    sheet.write('F%s' % row, '', borde)
    sheet.write('G%s' % row, '', borde)
    sheet.write('H%s' % row, '', borde)
    sheet.write('I%s' % row, '', borde)
    sheet.write('J%s' % row, '', borde)
    sheet.write('K%s' % row, '', borde)
    sheet.write('L%s' % row, '', borde)
    sheet.write('M%s' % row, '', borde)
    row += 1
    counter += 1

  row += 3
  sheet.write('A%s' % row, u'Q.F. Director Técnico', border_top)

  row += 2
  sheet.write('A%s' % row, u'Elaborado por', cabecera)
  sheet.write('B%s' % row, u'Revisado y Aprobado por:', cabecera)

  row += 1
  sheet.write('A%s' % row, '', borde)
  sheet.write('B%s' % row, '', borde)

  book.close()

  # construct response
  output.seek(0)
  response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
  response['Content-Disposition'] = "attachment; filename=anexo-%s.xlsx" % entrada.pk

  return response