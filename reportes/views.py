# -*- coding: utf-8 -*-

from django.shortcuts import render
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
from docx.shared import Cm, Mm, Pt
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
  sheet.write('L3', u'Reg. San.', bold)
  sheet.write('M3', u'FV Reg San', bold)
  sheet.write('N3', u'Condiciones de almacenamiento', bold)

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
    sheet.write('L%s' % row, entrada.lote.nrs)
    sheet.write('M%s' % row, entrada.lote.vrs, fecha)
    sheet.write('N%s' % row, '')

    row += 1

  sheet.autofilter(('A3:N%s' % row))
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

  output = StringIO.StringIO()

  book = Workbook(output)  

  book = Workbook(output)  
  sheet = book.add_worksheet(u'Anexo 1')
  sheet.set_landscape()
  sheet.set_paper(9)
  sheet.center_horizontally()

  bold = book.add_format({'bold': 1})
  bold_border = book.add_format({'bold': 1,'top': 1,'left': 1,'right': 1,'bottom': 1})
  fecha = book.add_format({'num_format': 'dd/mm/yy'})
  fecha_border = book.add_format({'num_format': 'dd/mm/yy','top': 1,'left': 1,'right': 1,'bottom': 1})
  money = book.add_format({'num_format': '0.00'})

  title = book.add_format({
    'bold': 1,
    'align': 'center',
    'size': 18
  })

  subtitle = book.add_format({
    'bold': 1,
    'align': 'center',
    'size': 11
  })

  subtitle2 = book.add_format({
    'bold': 1,
    'align': 'center',
    'size': 9
  })

  border = book.add_format({
    'top': 1,
    'left': 1,
    'right': 1,
    'bottom': 1
  })

  border_wrap = book.add_format({
    'top': 1,
    'left': 1,
    'right': 1,
    'bottom': 1,
  })

  border_bold_wrap = book.add_format({
    'top': 1,
    'left': 1,
    'right': 1,
    'bottom': 1,
    'bold': 1
  })

  sheet.merge_range('A1:L1', u'DROGUERIA HAMPI KALLPA EIRL', title)
  sheet.merge_range('A2:L2', u'N° 01', subtitle)
  sheet.merge_range('A3:L3', u'DROGUERIA HAMPI KALLPA EIRL', subtitle2)
  sheet.merge_range('A4:L4', u'REGISTRO DE RECEPCION Y CONFORMIDAD', subtitle2)

  # 1
  sheet.write('A6', u'Fecha:', bold)
  if entrada.fecha_entrada is not None:
    sheet.merge_range('B6:H6', entrada.fecha.strftime('%Y-%m-%d'), fecha)

  sheet.merge_range('I6:J6', u'Hora:', bold)
  if entrada.hora_entrada is not None:
    sheet.merge_range('K6:L6', entrada.hora_entrada)

  # 2
  sheet.merge_range('A7:L7', u'Q.F. Director Técnico: Q.F. Joel Alvarez Ochoa')

  # 3
  sheet.write('A8', u'Proveedor', bold)
  sheet.merge_range('B8:L8', entrada.proveedor.razon_social)

  # 4
  sheet.merge_range('A9:B9', u'Factura N°:', bold)
  sheet.merge_range('C9:H9', entrada.numero_factura)
  sheet.merge_range('I9:J9', u'Fecha Factura:', bold)
  sheet.merge_range('K9:L9', entrada.fecha_factura.strftime('%Y-%m-%d'), fecha)

  # 5
  sheet.merge_range('A10:B10', u'Guía de Remisión N°:', bold)
  sheet.merge_range('C10:H10', entrada.numero_guia)
  sheet.merge_range('I10:J10', u'Fecha Guía de Remisión:', bold)
  sheet.merge_range('K10:L10', entrada.fecha_guia.strftime('%Y-%m-%d'), fecha)

  ########
  # Tabla
  ########

  sheet.write('A12', u'Cant. Solicitada', bold_border)
  sheet.merge_range('B12:D12', u'Producto', bold_border)
  sheet.write('E12', u'Presentación', bold_border)
  sheet.write('F12', u'F/V', bold_border)
  sheet.write('G12', u'Lote', bold_border)
  sheet.write('H12', u'Fabricante', bold_border)
  sheet.write('I12', u'Cant. Recibida', bold_border)
  sheet.write('J12', u'N° Reg. San.', bold_border)
  sheet.write('K12', u'F.V. Reg. San.', bold_border)
  sheet.write('L12', u'Condiciones de almacenamiento', bold_border)                     

  row = 13
  for detalle in entrada.entradadetalle_set.all():

    comercial = detalle.lote.producto.comercial.upper()
    if comercial == '':
      the_prod = '%s' % (detalle.lote.producto.producto)
    else:
      the_prod = '%s / %s' % (detalle.lote.producto.producto, comercial)

    sheet.write('A%s' % row, detalle.cantidad, border)
    sheet.merge_range('B%s:D%s' % (row, row), the_prod, border_wrap)
    sheet.write('E%s' % row, '', border)
    try:
      sheet.write('F%s' % row, detalle.lote.vencimiento.strftime('%Y-%m-%d'), fecha_border)
    except:
      sheet.write('F%s' % row, '', border)
    sheet.write('G%s' % row, detalle.lote.numero, border)
    sheet.write('H%s' % row, detalle.lote.producto.marca, border)
    sheet.write('I%s' % row, detalle.cantidad, border)
    sheet.write('J%s' % row, detalle.lote.nrs, border)
    sheet.write('K%s' % row, detalle.lote.vrs, fecha_border)
    sheet.write('L%s' % row, '', border)
    row += 1

  sheet.autofilter(('A12:L%s' % row))

  row = row + 2

  sheet.write('A%s' % row, 'Entrega:', bold)
  sheet.write('B%s' % row, 'Proveedor o transportista')
  sheet.write('I%s' % row, 'Recibe:', bold)
  sheet.merge_range('J%s:L%s' % (row, row), u'Q.F. Director Técnico')



  # Libro 2

  sheet = book.add_worksheet(u'Anexo 2')
  sheet.set_landscape()
  sheet.set_paper(9)
  sheet.center_horizontally()

  sheet.merge_range('A1:R1', u'DROGUERIA HAMPI KALLPA EIRL', title)
  sheet.merge_range('A2:R2', u'ANEXO N° 02', subtitle)
  sheet.merge_range('A3:R3', u'ACTA DE EVALUACIÓN ORGANOLÉPTICA PARA EL INGRESO DE DISPOSITIVOS MÉDICOS AL ALMACÉN DE LA', subtitle2)
  sheet.merge_range('A4:R4', u'DROGUERIA HAMPI KALLPA EIRL', subtitle2)


  # 1
  sheet.write('A6', 'Fecha:')
  sheet.write('A7', 'Factura:')
  sheet.merge_range('B7:E7', entrada.numero_factura)
  sheet.merge_range('F7:G7', u'Guía de Remisión:')
  sheet.merge_range('H7:J7', entrada.numero_guia)
  sheet.write('K7', u'Proveedor:')
  sheet.merge_range('L7:R7', entrada.proveedor.razon_social)

  #####
  # Tabla
  #####
  sheet.merge_range('A10:A12', u'N°', border_bold_wrap)
  sheet.merge_range('B10:F11', u'Producto', border_bold_wrap)
  sheet.merge_range('G10:H11', u'Documentos Si(S) – No(N)', border_bold_wrap)
  sheet.merge_range('I10:J11', u'Embalaje adecuado', border_bold_wrap)
  sheet.merge_range('K10:L11', u'Envase inmediato adecuado', border_bold_wrap)
  sheet.merge_range('M10:R10', u'Envase médico', border_bold_wrap)
  sheet.merge_range('M11:N11', u'Rotulado adecuado', border_bold_wrap)
  sheet.merge_range('O11:P11', u'Aspecto Normal', border_bold_wrap)
  sheet.merge_range('Q11:R11', u'Cuerpos extraños', border_bold_wrap)

  sheet.merge_range('B12:D12', u'Descripción', border_bold_wrap)
  sheet.write('E12', u'Lote', border_bold_wrap)
  sheet.write('F12', u'FV', border_bold_wrap)
  sheet.write('G12', u'RS', border_bold_wrap)
  sheet.write('H12', u'Protocólo Análisis', border_bold_wrap)
  sheet.write('I12', u'Si', border_bold_wrap)
  sheet.write('J12', u'No', border_bold_wrap)
  sheet.write('K12', u'Si', border_bold_wrap)
  sheet.write('L12', u'No', border_bold_wrap)
  sheet.write('M12', u'Si', border_bold_wrap)
  sheet.write('N12', u'No', border_bold_wrap)
  sheet.write('O12', u'Si', border_bold_wrap)
  sheet.write('P12', u'No', border_bold_wrap)
  sheet.write('Q12', u'Si', border_bold_wrap)
  sheet.write('R12', u'No', border_bold_wrap)

  row = 13
  k = 1
  for detalle in entrada.entradadetalle_set.all():

    comercial = detalle.lote.producto.comercial.upper()
    if comercial == '':
      the_prod = '%s' % (detalle.lote.producto.producto)
    else:
      the_prod = '%s / %s' % (detalle.lote.producto.producto, comercial)

    sheet.write('A%s' % row, k, border)

    sheet.merge_range('B%s:D%s' % (row, row), the_prod, border_wrap)
    sheet.write('E%s' % row, detalle.lote.numero, border)
    try:
      sheet.write('F%s' % row, detalle.lote.vencimiento.strftime('%Y-%m-%d'), fecha_border)
    except:
      sheet.write('F%s' % row, '', border)
    sheet.write('G%s' % row, detalle.lote.nrs, border)
    sheet.write('H%s' % row, '', border)
    sheet.write('I%s' % row, '', border)
    sheet.write('J%s' % row, '', border)
    sheet.write('K%s' % row, '', border)
    sheet.write('L%s' % row, '', border)
    sheet.write('M%s' % row, '', border)
    sheet.write('N%s' % row, '', border)
    sheet.write('O%s' % row, '', border)
    sheet.write('P%s' % row, '', border)
    sheet.write('Q%s' % row, '', border)
    sheet.write('R%s' % row, '', border)
    
    row += 1
    k += 1

  sheet.autofilter(('A12:R%s' % row))

  row = row + 2

  sheet.write('A%s' % row, u'Observación:')

  row = row + 5

  sheet.merge_range('H%s:K%s' % (row,row), u'Director Técnico', bold)

  book.close()

  # construct response
  output.seek(0)
  response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
  response['Content-Disposition'] = "attachment; filename=anexo-%s.xlsx" % entrada.pk

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
    fila['egreso'] = 0
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
    fila['ingreso'] = 0
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
  sheet = book.add_worksheet(u'Kardex Lote')

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

@login_required
def kardex2_excel(request, id):
  p = Producto.objects.get(pk = id)
  productos = Producto.objects.filter(producto = p.producto)
  historia = []
  for producto in productos:
    lotes = producto.lote_set.all()
    for lote in lotes:
      entradas = lote.entradadetalle_set.all()
      ventas = lote.ventadetalle_set.all()
      for entrada in entradas:
        fila = {}
        fila['fecha'] = entrada.entrada_padre.fecha_guia
        fila['guia'] = entrada.entrada_padre.numero_guia
        fila['ingreso'] = entrada.cantidad
        fila['egreso'] = 0
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
        fila['ingreso'] = 0
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
  sheet = book.add_worksheet(u'Kardex Producto')

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
  return render(request, 'front/vendidos.html', context)


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

  inicial = request.POST.get('inicial')
  final = request.POST.get('final')

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

  hasta = 'E'
  sheet.merge_range('A1:%s1' % hasta, u'Relación de Productos Vendidos Hampi Kallpa', title)
  sheet.merge_range('A2:%s2' % hasta, u'Desde %s hasta %s' % (inicial.strftime('%d/%m/%Y'), final.strftime('%d/%m/%Y')), title)

  sheet.write('A3', u'Producto', bold)
  sheet.write('B3', u'Lote', bold)
  sheet.write('C3', u'Cuando', bold)
  sheet.write('D3', u'Cliente', bold)
  sheet.write('E3', u'RUC', bold)

  row = 4
  for vendido in vendidos:


    sheet.write('A%s' % row, vendido.lote.producto.producto)
    sheet.write('B%s' % row, vendido.lote.numero)
    sheet.write('C%s' % row, vendido.registro_padre.fecha_factura, fecha)
    sheet.write('D%s' % row, vendido.registro_padre.cliente.razon_social)
    sheet.write('E%s' % row, vendido.registro_padre.cliente.numero_documento)
    
    row += 1

  sheet.autofilter(('A3:%s%s' % (hasta, row)))
  book.close()

  # construct response
  output.seek(0)
  response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
  response['Content-Disposition'] = "attachment; filename=productos-vendidos-fecha-%s.xlsx" % date.today()

  return response

@login_required
def excel_proveedores_fecha(request):


  output = StringIO.StringIO()

  book = Workbook(output)  
  sheet = book.add_worksheet(u'Proveedores')

  inicial = request.POST.get('inicial')
  final = request.POST.get('final')

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

  rows = Entrada.objects.filter(fecha_factura__range = (inicial, final))

  hasta = 'E'
  sheet.merge_range('A1:%s1' % hasta, u'Relación de Proveedores que han vendido a Hampi Kallpa', title)
  sheet.merge_range('A2:%s2' % hasta, u'Desde %s hasta %s' % (inicial.strftime('%d/%m/%Y'), final.strftime('%d/%m/%Y')), title)

  sheet.write('A3', u'Proveedor', bold)
  sheet.write('B3', u'RUC', bold)
  sheet.write('C3', u'Fecha', bold)
  sheet.write('D3', u'Factura', bold)
  sheet.write('E3', u'Guía', bold)

  row = 4
  for fila in rows:


    sheet.write('A%s' % row, fila.proveedor.razon_social)
    sheet.write('B%s' % row, fila.proveedor.ruc)
    sheet.write('C%s' % row, fila.fecha_factura, fecha)
    sheet.write('D%s' % row, fila.numero_factura)
    sheet.write('E%s' % row, fila.numero_guia)
    
    row += 1

  sheet.autofilter(('A3:%s%s' % (hasta, row)))
  book.close()

  # construct response
  output.seek(0)
  response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
  response['Content-Disposition'] = "attachment; filename=proveedores-vendieron-fecha-%s.xlsx" % date.today()

  return response

@login_required
def excel_clientes_fecha(request):


  output = StringIO.StringIO()

  book = Workbook(output)  
  sheet = book.add_worksheet(u'Clientes')

  inicial = request.POST.get('inicial')
  final = request.POST.get('final')

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

  rows = Venta.objects.filter(fecha_factura__range = (inicial, final))

  hasta = 'E'
  sheet.merge_range('A1:%s1' % hasta, u'Relación de Clientes atendidos por Hampi Kallpa', title)
  sheet.merge_range('A2:%s2' % hasta, u'Desde %s hasta %s' % (inicial.strftime('%d/%m/%Y'), final.strftime('%d/%m/%Y')), title)

  sheet.write('A3', u'Cliente', bold)
  sheet.write('B3', u'RUC', bold)
  sheet.write('C3', u'Fecha', bold)
  sheet.write('D3', u'Factura', bold)
  sheet.write('E3', u'Guia', bold)

  row = 4
  for fila in rows:


    sheet.write('A%s' % row, fila.cliente.razon_social)
    sheet.write('B%s' % row, fila.cliente.numero_documento)
    sheet.write('C%s' % row, fila.fecha_factura, fecha)
    sheet.write('D%s' % row, fila.numero_factura)
    sheet.write('E%s' % row, fila.numero_guia)
    
    row += 1

  sheet.autofilter(('A3:%s%s' % (hasta, row)))
  book.close()

  # construct response
  output.seek(0)
  response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
  response['Content-Disposition'] = "attachment; filename=clientes-atendidos-fecha-%s.xlsx" % date.today()

  return response

from front.printable import ImpresionAnexo
from io import BytesIO
@login_required
def anexo_pdf_print(request, id):
  entrada = Entrada.objects.get(id = id)

  response = HttpResponse(content_type='application/pdf')

  buffer = BytesIO()

  report = ImpresionAnexo(buffer, 'A4')
  pdf = report.imprimir(entrada)

  response.write(pdf)
  return response
