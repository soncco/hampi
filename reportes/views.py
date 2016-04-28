# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
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

from core.models import Producto, Gasto, Cliente, Proveedor, Lote

from front.utils import diff_dates

from docx import Document
from docx.shared import Cm, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT

from operator import itemgetter

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
  sheet.write('G3', u'Total Venta', bold)
  sheet.write('H3', u'Almacén', bold)

  row = 4
  for st in stock:

    sheet.write('A%s' % row, st.lote.producto.codigo)
    sheet.write('B%s' % row, st.lote.producto.producto)
    sheet.write('C%s' % row, st.lote.numero)
    sheet.write('D%s' % row, st.lote.vencimiento)
    sheet.write('E%s' % row, st.unidades)
    sheet.write('F%s' % row, st.lote.producto.precio_unidad, money)
    sheet.write_formula('G%s' % row, '{=E%s*F%s}' % (row, row))
    sheet.write('H%s' % row, st.en_almacen.nombre)

    row += 1

  sheet.autofilter(('A3:H%s' % row))
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
  document = Document()

  section = document.sections[-1]
  section.left_margin = Cm(2)
  section.top_margin = Cm(2)
  section.right_margin = Cm(2)
  section.bottom_margin = Cm(2)
  section.page_width = Mm(210)
  section.page_height = Mm(297)
  section.orientation = WD_ORIENT.PORTRAIT

  p = document.add_paragraph()
  p.add_run(u'Anexo N° -A').bold = True
  p.alignment = WD_ALIGN_PARAGRAPH.CENTER

  p = document.add_paragraph()
  p.add_run(u'DROGUERÍA HAMPI KALLPA E.I.R.L.').bold = True
  p.alignment = WD_ALIGN_PARAGRAPH.CENTER
  
  p = document.add_paragraph()
  p.add_run(u'ACTA DE RECEPCIÓN Y CONFORMIDAD').bold = True
  p.alignment = WD_ALIGN_PARAGRAPH.CENTER
  document.add_paragraph()

  p = document.add_paragraph()
  p.add_run(u'Fecha: ').bold = True
  if entrada.fecha_entrada is not None:
    p.add_run(entrada.fecha_entrada.strftime('%d %b %Y'))
  p.add_run('                           ')
  p.add_run(u'Hora: ').bold = True
  if entrada.hora_entrada is not None:
    p.add_run(entrada.hora_entrada)

  p = document.add_paragraph()
  p.add_run(u'Q.F. Director Técnico:').bold = True

  p = document.add_paragraph()
  p.add_run(u'Proveedor: ').bold = True
  p.add_run(entrada.proveedor.razon_social)

  p = document.add_paragraph()
  p.add_run(u'Factura Nro: ').bold = True
  p.add_run(entrada.numero_factura)
  p.add_run('                         ')
  p.add_run(u'Fecha Factura: ').bold = True
  p.add_run(entrada.fecha_factura.strftime('%d %b %Y'))

  p = document.add_paragraph()
  p.add_run(u'Guía de Remisión Nro: ').bold = True
  p.add_run(entrada.numero_guia)
  p.add_run('                         ')
  p.add_run(u'Fecha G/R: ').bold = True
  p.add_run(entrada.fecha_guia.strftime('%d %b %Y'))
  document.add_paragraph()

  table = document.add_table(rows=1, cols=8)
  table.style = 'TableGrid'
  hdr_cells = table.rows[0].cells
  hdr_cells[0].text = u'CANT'
  hdr_cells[1].text = u'F.F.'
  hdr_cells[2].text = u'DESCRIPCIÓN'
  hdr_cells[3].text = u'FABRICANTE'
  hdr_cells[4].text = u'F/V'
  hdr_cells[5].text = u'LOTE'
  hdr_cells[6].text = u'N de R.S'
  hdr_cells[7].text = u'Vencimiento R.S.'
  hdr_cells[2].width = Cm(8)
  for detalle in entrada.entradadetalle_set.all():
      row_cells = table.add_row().cells
      row_cells[0].text = str(detalle.cantidad)
      row_cells[1].text = detalle.lote.producto.unidad_medida
      row_cells[2].text = detalle.lote.producto.producto
      row_cells[3].text = detalle.lote.producto.marca
      try:
        row_cells[4].text = detalle.lote.vencimiento.strftime('%d/%m/%Y')
      except:
        row_cells[4].text = ''
      row_cells[5].text = detalle.lote.numero
      row_cells[6].text = detalle.lote.nrs if detalle.lote.nrs is not None else ''
      row_cells[7].text = detalle.lote.vrs if detalle.lote.vrs is not None else ''
      row_cells[2].width = Cm(12)


  document.add_paragraph()
  document.add_paragraph()
  p = document.add_paragraph('____________________________')
  p = document.add_paragraph(u'Q.F. Director Técnico')


  # Anexo 2.
  section = document.add_section()
  section.left_margin = Cm(2)
  section.top_margin = Cm(2)
  section.right_margin = Cm(2)
  section.bottom_margin = Cm(2)
  section.page_width = Mm(210)
  section.page_height = Mm(297)
  section.orientation = WD_ORIENT.PORTRAIT

  p = document.add_paragraph()
  p.add_run(u'Anexo N° -B').bold = True
  p.alignment = WD_ALIGN_PARAGRAPH.CENTER

  p = document.add_paragraph()
  p.add_run(u'ACTA DE RECEPCIÓN Y EVALUACIÓN ORGANOLÉPTICA PARA EL INGRESO DE PRODUCTOS FARMACÉUTICOS Y AFINES AL ALMACEN DE LA DROGUERIA "HAMPI KALLPA E.I.R.L."').bold = True
  p.alignment = WD_ALIGN_PARAGRAPH.CENTER

  p = document.add_paragraph()
  p.add_run(u'Fecha: ').bold = True
  if entrada.fecha_entrada is not None:
    p.add_run(entrada.fecha_entrada.strftime('%d %b %Y'))

  p = document.add_paragraph()
  p.add_run(u'Factura Nro: ').bold = True
  p.add_run(entrada.numero_factura)
  p.add_run(u'                   ')
  p.add_run(u'Guía de Remisión Nro: ').bold = True
  p.add_run(entrada.numero_guia)
  p.add_run(u'                   ')
  p.add_run(u'Proveedor: ').bold = True
  p.add_run(entrada.proveedor.razon_social)
  document.add_paragraph()

  table = document.add_table(rows=2, cols=13)
  table.style = 'TableGrid'
  
  hdr_cells = table.rows[0].cells
  hdr_cells[0].text = u''
  hdr_cells[1].text = u'Producto'
  hdr_cells[4].text = u'Documentos'
  hdr_cells[6].text = u'Embalaje Adecuado'
  hdr_cells[8].text = u'Envase inmediato adecuado'
  hdr_cells[10].text = u'Contenido'

  #hdr_cells[1].merge(hdr_cells[2])
  hdr_cells[1].merge(hdr_cells[3])
  hdr_cells[4].merge(hdr_cells[5])
  hdr_cells[6].merge(hdr_cells[7])
  hdr_cells[8].merge(hdr_cells[9])
  hdr_cells[10].merge(hdr_cells[12])


  hdr_cells = table.rows[1].cells
  hdr_cells[0].text = u'N°'
  hdr_cells[1].text = u'Descripción'
  hdr_cells[2].text = u'Lote'
  hdr_cells[3].text = u'FV'
  hdr_cells[4].text = u'RS'
  hdr_cells[5].text = u'Protocolo Análisis'
  hdr_cells[6].text = u'Si'
  hdr_cells[7].text = u'No'
  hdr_cells[8].text = u'Si'
  hdr_cells[9].text = u'No'
  hdr_cells[10].text = u'Color'
  hdr_cells[11].text = u'Aspecto'
  hdr_cells[12].text = u'No cuerpos extraños'
  hdr_cells[1].width = Cm(7)

  counter = 1
  for detalle in entrada.entradadetalle_set.all():
      row_cells = table.add_row().cells
      row_cells[0].text = str(counter)
      row_cells[1].text = detalle.lote.producto.producto
      row_cells[2].text = detalle.lote.numero
      try:
        row_cells[3].text = detalle.lote.vencimiento.strftime('%d/%m/%Y')
      except:
        row_cells[3].text = ''
      counter += 1

  document.add_paragraph()
  document.add_paragraph()
  p = document.add_paragraph('____________________________')
  p = document.add_paragraph(u'Q.F. Director Técnico')
  
  from cStringIO import StringIO
  f = StringIO()
  document.save(f)
  length = f.tell()
  f.seek(0)
  response = HttpResponse(
      f.getvalue(),
      content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  )
  response['Content-Disposition'] = 'attachment; filename=anexo%s.docx' % entrada.pk
  response['Content-Length'] = length
  return response

@login_required
def kardex_excel(request, id):
  lote = Lote.objects.get(pk = id)
  entradas = lote.entradadetalle_set.all()
  ventas = lote.ventadetalle_set.all()
  historia = []
  for entrada in entradas:
    fila = {}
    fila['fecha'] = entrada.entrada_padre.fecha_guia
    fila['guia'] = entrada.entrada_padre.numero_guia
    fila['ingreso'] = entrada.cantidad
    fila['egreso'] = ''
    fila['cliente'] = ''
    fila['proveedor'] = entrada.entrada_padre.proveedor.razon_social
    fila['mi_guia'] = ''
    fila['lote'] = entrada.lote.numero
    fila['vencimiento'] = entrada.lote.vencimiento
    fila['nro'] = entrada.entrada_padre.pk

    historia.append(fila)

  for venta in ventas:
    fila = {}
    fila['fecha'] = venta.registro_padre.fecha_traslado
    fila['guia'] = ''
    fila['ingreso'] = ''
    fila['egreso'] = venta.cantidad
    fila['cliente'] = venta.registro_padre.cliente.razon_social
    fila['proveedor'] = ''
    fila['mi_guia'] = venta.registro_padre.numero_guia
    fila['lote'] = venta.lote.numero
    fila['vencimiento'] = venta.lote.vencimiento
    fila['nro'] = venta.registro_padre.pk

    historia.append(fila)

  nueva_historia = sorted(historia, key=itemgetter('fecha')) 
  
  output = StringIO.StringIO()

  book = Workbook(output)  
  sheet = book.add_worksheet(u'Kardex')

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

  sheet.merge_range('A1:K1', u'REGISTRO DE PRODUCTOS FARMACEUTICOS - KARDEX INFORMÁTICO', title)
  sheet.merge_range('A2:K2', u'DROGUERÍA HAMPI KALLPA E.I.R.L.', title)

  sheet.write('A4', u'PRODUCTO: %s' % lote.producto.producto, bold)
  sheet.write('A5', u'PRESENTACIÓN: %s' % lote.producto.unidad_medida, bold)

  sheet.write('A7', u'Fecha', bold)
  sheet.write('B7', u'Guía de Remisión N° Proveedor', bold)
  sheet.write('C7', u'Ingreso', bold)
  sheet.write('D7', u'Egreso', bold)
  sheet.write('E7', u'Cliente', bold)
  sheet.write('F7', u'Proveedor', bold)
  sheet.write('G7', u'Guía de Remisión N°', bold)
  sheet.write('H7', u'Lote', bold)
  sheet.write('I7', u'FV', bold)
  sheet.write('J7', u'Saldo', bold)
  sheet.write('K7', u'NRO', bold)

  row = 8
  for item in nueva_historia:
    sheet.write('A%s' % row, item['fecha'].strftime('%Y-%m-%d'), fecha)
    sheet.write('B%s' % row, item['guia'])
    sheet.write('C%s' % row, item['ingreso'])
    sheet.write('D%s' % row, item['egreso'])
    sheet.write('E%s' % row, item['cliente'])
    sheet.write('F%s' % row, item['proveedor'])
    sheet.write('G%s' % row, item['mi_guia'])
    sheet.write('H%s' % row, item['lote'])
    sheet.write('I%s' % row, item['vencimiento'].strftime('%Y-%m-%d'), fecha)
    if row == 8:
      sheet.write('J%s' % row, item['ingreso'])
    else:
      sheet.write_formula('J%s' % row, '=J%s+C%s-D%s' % (row-1, row, row))
    sheet.write('K%s' % row, item['nro'])
    row += 1

  sheet.autofilter(('A7:K%s' % row))
  book.close()

  # construct response
  output.seek(0)
  response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
  response['Content-Disposition'] = "attachment; filename=kardex-%s.xlsx" % lote.pk

  return response


def vendidos(request):
  vendidos = VentaDetalle.objects.values('lote__producto').distinct()

  productos = []

  for vendido in vendidos:
    p = Producto.objects.get(pk = vendido['lote__producto'])
    productos.append(p)

  context = {'productos': productos}
  return render_to_response('vendidos.html', context, context_instance = RequestContext(request))


@login_required
def excel_vendidos(request):

  output = StringIO.StringIO()

  book = Workbook(output)  
  sheet = book.add_worksheet(u'Productos Vendidos')

  bold = book.add_format({'bold': 1})
  fecha = book.add_format({'num_format': 'dd/mm/yy'})
  
  title = book.add_format({
    'bold': 1,
    'align': 'center',
    'font_color': 'white',
    'fg_color': '#18bc9c',
  })

  vendidos = VentaDetalle.objects.values('lote__producto').distinct()

  productos = []

  for vendido in vendidos:
    p = Producto.objects.get(pk = vendido['lote__producto'])
    productos.append(p)
  

  sheet.merge_range('A1:F1', u'Relación de Productos Hampi Kallpa', title)

  sheet.merge_range('A3:F3', u'Producto', bold)

  row = 4
  for producto in productos:

    sheet.merge_range('A%s:F%s' % (row, row), producto.producto)
    
    row += 1

  sheet.autofilter(('A3:F%s' % row))
  book.close()

  # construct response
  output.seek(0)
  response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
  response['Content-Disposition'] = "attachment; filename=productos-vendidos-%s.xlsx" % date.today()

  return response

@login_required
def excel_vendidos_fecha(request):

  output = StringIO.StringIO()

  book = Workbook(output)  
  sheet = book.add_worksheet(u'Productos Vendidos por fecha')

  inicial = request.GET.get('inicial')
  final = request.GET.get('final')

  inicial = datetime.datetime.strptime(inicial, "%Y-%m-%d")
  final = datetime.datetime.strptime(final, "%Y-%m-%d")

  bold = book.add_format({'bold': 1})
  fecha = book.add_format({'num_format': 'dd/mm/yy'})
  
  title = book.add_format({
    'bold': 1,
    'align': 'center',
    'font_color': 'white',
    'fg_color': '#18bc9c',
  })

  vendidos = VentaDetalle.objects.filter(registro_padre__fecha_factura__range = (inicial, final))

  sheet.merge_range('A1:B1', u'Relación de Productos Vendidos Hampi Kallpa', title)
  sheet.merge_range('A2:B2', u'Desde %s hasta %s' % (inicial.strftime('%d/%m/%Y'), final.strftime('%d/%m/%Y')), title)

  sheet.write('A3', u'Producto', bold)
  sheet.write('B3', u'Lote', bold)

  row = 4
  for vendido in vendidos:

    print vendido

    sheet.write('A%s' % row, vendido.lote.producto.producto)
    sheet.write('B%s' % row, vendido.lote.numero)
    
    row += 1

  sheet.autofilter(('A3:B%s' % row))
  book.close()

  # construct response
  output.seek(0)
  response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
  response['Content-Disposition'] = "attachment; filename=productos-vendidos-fecha-%s.xlsx" % date.today()

  return response