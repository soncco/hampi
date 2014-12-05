# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

from django.db.models import Q

from django.contrib.auth.models import User

from django_xhtml2pdf.utils import generate_pdf

import reportlab.rl_config
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from unidecode import unidecode
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from numword.numword_es import cardinal

from decimal import *
from datetime import date

from ventas.forms import VentaForm, DetalleFormSet, CotizacionForm, CotizacionDetalleFormSet
from ventas.models import Venta, VentaDetalle, Deuda, Amortizacion, Cotizacion, CotizacionDetalle
from ventas.utils import total_amortizaciones, saldo_deuda

from almacen.forms import EntradaForm, EntradaDetalleFormSet, SalidaForm, SalidaDetalleFormSet
from almacen.models import Almacen, Entrada, Salida, Stock
from almacen.utils import generar_salida_venta, entrada_stock, salida_stock, total_monto_stock, total_monto_stock_real

from core.models import Gasto, Cliente, Proveedor, TipoGasto, Lote, Producto
from core.forms import ProductoForm

from .utils import total_gastos, total_contados, total_amortizacion, total_liquidacion, diff_dates

# Ventas
@login_required
def venta(request):
  if request.method == 'POST':
    venta_form = VentaForm(request.POST)
    detalle_form = DetalleFormSet(request.POST)

    if venta_form.is_valid() and detalle_form.is_valid():
      instance = venta_form.save()
      detalle_form.instance = instance
      detalle_form.save()

      salida = generar_salida_venta(instance)
      salida_stock(salida)

      if instance.tipo_venta == 'P':
        monto = request.POST.get('monto')
        if monto == '':
          monto = 0

        saldo = instance.total_venta - Decimal(monto)
        deuda = Deuda(registro_padre = instance, total = saldo, estado = 'D')
        deuda.save()

        amortizacion = Amortizacion(deuda = deuda, fecha = instance.fecha_factura, monto = Decimal(monto), saldo = saldo, recibido_por = request.user)
        amortizacion.save()
        messages.success(request, 'Se ha creado también una deuda y una amortización.')
      messages.success(request, 'Se ha guardado la venta y se ha creado una salida.')

      return HttpResponseRedirect(reverse('ventas'))

    else:
      print entrada_form.errors
      print detalle_form.errors

  almacenes = Almacen.objects.all()
  context = {'detalle_form': DetalleFormSet, 'almacenes': almacenes}
  return render_to_response('venta-nuevo.html', context, context_instance = RequestContext(request))

@login_required
def ventas(request):
  ventas = Venta.objects.all().order_by('-id')
  for venta in ventas:
    try:
      venta.saldo = saldo_deuda(venta.deuda)
    except:
      venta.saldo = 'Sin deuda'
  context = {'ventas': ventas}
  return render_to_response('ventas.html', context, context_instance = RequestContext(request))

@login_required
def venta_view(request, id):
  venta = Venta.objects.get(pk = id)
  context = {'venta': venta}
  if venta.tipo_venta == 'P':
    amortizaciones = Amortizacion.objects.filter(deuda = venta.deuda.pk)
    context['amortizaciones'] = amortizaciones
  return render_to_response('venta-ver.html', context, context_instance = RequestContext(request))

@login_required
def venta_print(request, id):
  venta = Venta.objects.get(id = id)

  resp = HttpResponse(content_type = 'application/pdf')
  context = {'venta': venta}
  if venta.tipo_venta == 'P':
    amortizaciones = Amortizacion.objects.filter(deuda = venta.deuda.pk)
    context['amortizaciones'] = amortizaciones
  result = generate_pdf('pdf/venta.html', file_object = resp, context = context)
  return result

@login_required
def venta_factura_print(request, id):
  venta = Venta.objects.get(id = id)

  response = HttpResponse(content_type = 'application/pdf')

  reportlab.rl_config.warnOnMissingFontGlyphs = 0
  fontsize = 8

  pdfmetrics.registerFont(TTFont('A1979', 'A1979.ttf'))
  p = canvas.Canvas(response, pagesize = A4)
  p.setFont('A1979', fontsize)

  styles = getSampleStyleSheet()
  style = ParagraphStyle('A1979')
  style.fontName = 'A1979'
  style.fontSize = fontsize

  # Cliente.

  top = 473
  left = 87
  story = []
  story.append(Paragraph(unidecode(venta.cliente.razon_social.upper()), style))
  f = Frame(left, top, 300, 200, showBoundary = 0)
  f.addFromList(story, p)

  top = 653
  left = 63
  p.drawString(left, top - 15, venta.cliente.numero_documento)

  top = 433
  left = 80
  story = []
  story.append(Paragraph('%s - %s - %s - %s' % (venta.cliente.direccion.upper(), venta.cliente.ciudad.upper(), venta.cliente.distrito.upper(), venta.cliente.departamento.upper()), style))
  f = Frame(left, top, 270, 200, showBoundary = 0)
  f.addFromList(story, p)

  # Guía.
  top = 660
  left = 490
  p.drawString(left, top, venta.fecha_emision.strftime('%d/%m/%Y'))
  p.drawString(left, top - 45, venta.numero_guia)

  # Meta.
  left = 50
  top = 573
  p.drawString(left-5, top, venta.cliente.codcliente.upper())
  p.drawString(left + 110, top, venta.orden_compra.upper())
  p.drawString(left + 190, top, venta.condiciones.upper())
  p.drawString(left + 292, top, venta.vencimiento.strftime('%d/%m/%Y'))
  #p.drawString(left + 400, top, venta.vendedor.first_name.upper())
  p.drawString(left + 520, top, venta.hora)
  
  # Detalles.
  top = 530
  left = 30
  for detalle in venta.ventadetalle_set.all():
    tab = 25
    p.drawString(left, top, detalle.lote.producto.codigo)
    p.drawRightString(left+30, top, str(detalle.cantidad))
    p.drawString(left+50, top, detalle.lote.producto.unidad_medida.upper())

    the_prod = '%s - %s' % (unidecode(detalle.lote.producto.producto.upper()), unidecode(detalle.lote.producto.marca.upper()))

    if len(the_prod) > 58:
      top = top - 186
      story = []
      story.append(Paragraph(the_prod, style))
      f = Frame(left+80, top, 270, 200, showBoundary = 0)
      f.addFromList(story, p)
      top = top + 186

      p.drawString(left+90, top-23, 'LOTE: %s' % detalle.lote.numero)
      p.drawString(left+300, top-23, 'VCTO: %s' % detalle.lote.vencimiento.strftime('%d/%m/%Y'))
      tab = 40
    else:
      p.drawString(left+80, top, the_prod)
      p.drawString(left+90, top-10, 'LOTE: %s' % detalle.lote.numero)
      p.drawString(left+300, top-10, 'VCTO: %s' % detalle.lote.vencimiento.strftime('%d/%m/%Y'))


    p.drawRightString(left+470, top, '%.3f' % detalle.precio_unitario)
    p.drawRightString(left+530, top, '%.3f' % detalle.total)

    top -= tab

  # Cardinal.
  top = 138
  p.drawString(left+30, top, cardinal(float(venta.total_venta)).upper())

  # IGV.
  top = 115
  left = 550

  igv = float(venta.total_venta) * 0.18
  subtotal = float(venta.total_venta) - igv

  top = 115
  p.drawRightString(left, top, '%.2f' % subtotal)
  p.drawRightString(left, top - 15, '%.2f' % igv)
  p.drawRightString(left, top - 30, '%.2f' % venta.total_venta)

  p.showPage()
  p.save()

  return response

@login_required
def venta_guia_print(request, id):
  venta = Venta.objects.get(id = id)

  response = HttpResponse(content_type = 'application/pdf')

  reportlab.rl_config.warnOnMissingFontGlyphs = 0
  fontsize = 8

  pdfmetrics.registerFont(TTFont('A1979', 'A1979.ttf'))
  p = canvas.Canvas(response, pagesize = A4)
  p.setFont('A1979', fontsize)

  styles = getSampleStyleSheet()
  style = ParagraphStyle('A1979')
  style.fontName = 'A1979'
  style.fontSize = fontsize

  # Fechas.
  top = 687
  left = 100

  p.drawString(left, top, venta.fecha_emision.strftime('%d/%m/%Y'))
  p.drawString(left + 150, top, venta.fecha_traslado.strftime('%d/%m/%Y'))

  # Meta.
  top = 655
  left = 40
  p.drawString(left, top, venta.condiciones)
  p.drawString(left + 100, top, venta.orden_compra)
  p.drawString(left + 200, top, venta.fecha_factura.strftime('%d/%m/%Y'))

  # Direcciones.
  top = 440
  left = 78
  story = []
  story.append(Paragraph(venta.procedencia.upper(), style))
  f = Frame(left, top, 260, 200, showBoundary = 0)
  f.addFromList(story, p)

  story = []
  story.append(Paragraph(venta.llegada.upper(), style))
  f = Frame(left + 294, top, 230, 200, showBoundary = 0)
  f.addFromList(story, p)

  # Destino y Transporte.
  top = 384
  left = 70
  story = []
  story.append(Paragraph(unidecode(venta.cliente.razon_social.upper()), style))
  f = Frame(left, top, 260, 200, showBoundary = 0)
  f.addFromList(story, p)

  top = 565
  p.drawString(left, top - 15, venta.cliente.numero_documento)

  left = 430
  top = 570
  p.drawString(left, top - 10, unidecode(venta.vehiculo.upper()))
  p.drawString(left, top - 20, unidecode(venta.inscripcion.upper()))
  p.drawString(left, top - 30, unidecode(venta.licencia.upper()))

  # Detalles.
  top = 495
  left = 30
  for detalle in venta.ventadetalle_set.all():
    p.drawString(left, top, detalle.lote.producto.codigo)
    p.drawRightString(left+30, top, str(detalle.cantidad))
    p.drawString(left+70, top, detalle.lote.producto.unidad_medida.upper())
    p.drawString(left+110, top, '%s - %s' % (unidecode(detalle.lote.producto.producto.upper()), unidecode(detalle.lote.producto.marca.upper())))
    p.drawString(left+110, top-10, 'LOTE: %s' % detalle.lote.numero)
    p.drawString(left+300, top-10, 'VCTO: %s' % detalle.lote.vencimiento.strftime('%d/%m/%Y'))

    top -= 25

  # Comprobates y transporte.
  top = 115
  left = 80
  p.drawString(left, top, 'FACTURA')
  p.drawString(left+140, top, venta.numero_factura)

  top = 128
  p.drawString(left+280, top, unidecode(venta.transportista.upper()))
  p.drawString(left+280, top-15, venta.ruc_transportista)


  p.showPage()
  p.save()

  return response

@login_required
def deudas(request):
  deudas = Deuda.objects.all().order_by('-id')
  for deuda in deudas:
    deuda.atrasado = diff_dates(deuda.registro_padre.fecha_factura, date.today())
    deuda.saldo = saldo_deuda(deuda)

  context = {'deudas': deudas}
  return render_to_response('deudas.html', context, context_instance = RequestContext(request))

@login_required
def amortizacion(request, id):
  deuda = Deuda.objects.get(pk = id)
  if request.method == 'POST':
    fecha = request.POST.get('fecha')
    monto = Decimal(request.POST.get('monto'))
    saldo = deuda.registro_padre.total_venta - total_amortizaciones(deuda) - monto

    amortizacion = Amortizacion(deuda = deuda, fecha = fecha, monto = monto, saldo = saldo, recibido_por = request.user)
    amortizacion.save()

    if saldo <= 0:
      deuda.estado = 'C'
      deuda.save()

    messages.success(request, 'Se ha guardado la amortizacion.')

    return HttpResponseRedirect(reverse('venta_view', args = [deuda.id]))

  saldo = deuda.registro_padre.total_venta - total_amortizaciones(deuda)
  context = {'deuda': deuda, 'saldo': saldo}
  return render_to_response('amortizacion.html', context, context_instance = RequestContext(request))

# Entradas
@login_required
def entradas(request):
  entradas = Entrada.objects.all().order_by('-id')
  context = {'entradas': entradas}
  return render_to_response('entradas.html', context, context_instance = RequestContext(request))

def entrada(request):
  if request.method == 'POST':
    entrada_form = EntradaForm(request.POST)
    detalle_form = EntradaDetalleFormSet(request.POST)

    if entrada_form.is_valid() and detalle_form.is_valid():
      instance = entrada_form.save()
      detalle_form.instance = instance
      detalle_form.save()

      entrada_stock(instance)

      messages.success(request, 'Se ha guardado la entrada y se ha actualizado el Stock.')
      return HttpResponseRedirect(reverse('entradas'))

  almacenes = Almacen.objects.all()
  context = {'detalle_form': EntradaDetalleFormSet, 'almacenes': almacenes}
  return render_to_response('entrada-nuevo.html', context, context_instance = RequestContext(request))

@login_required
def entrada_view(request, id):
  entrada = Entrada.objects.get(pk = id)
  context = {'entrada': entrada}
  return render_to_response('entrada-ver.html', context, context_instance = RequestContext(request))

@login_required
def entrada_print(request, id):
  entrada = Entrada.objects.get(id = id)

  resp = HttpResponse(content_type = 'application/pdf')
  context = {'entrada': entrada}
  result = generate_pdf('pdf/entrada.html', file_object = resp, context = context)
  return result

# Salidas
@login_required
def salidas(request):
  salidas = Salida.objects.all().order_by('-id')
  context = {'salidas': salidas}
  return render_to_response('salidas.html', context, context_instance = RequestContext(request))

def salida(request):
  if request.method == 'POST':
    salida_form = SalidaForm(request.POST)
    detalle_form = SalidaDetalleFormSet(request.POST)

    if salida_form.is_valid() and detalle_form.is_valid():
      instance = salida_form.save()
      detalle_form.instance = instance
      detalle_form.save()

      salida_stock(instance)

      messages.success(request, 'Se ha guardado la salida y se ha actualizado el Stock.')
      return HttpResponseRedirect(reverse('salidas'))

    else:
      print salida_form.errors
      print detalle_form.errors

  almacenes = Almacen.objects.all()
  context = {'detalle_form': SalidaDetalleFormSet, 'almacenes': almacenes}
  return render_to_response('salida-nuevo.html', context, context_instance = RequestContext(request))

@login_required
def salida_view(request, id):
  salida = Salida.objects.get(pk = id)
  context = {'salida': salida}
  return render_to_response('salida-ver.html', context, context_instance = RequestContext(request))

@login_required
def salida_print(request, id):
  salida = Salida.objects.get(id = id)

  resp = HttpResponse(content_type = 'application/pdf')
  context = {'salida': salida}
  result = generate_pdf('pdf/salida.html', file_object = resp, context = context)
  return result

# Gastos
@login_required
def gastos(request):
  gastos = Gasto.objects.all().order_by('-id')
  context = {'gastos': gastos}
  return render_to_response('gastos.html', context, context_instance = RequestContext(request))

@login_required
def gasto(request):
  if request.method == 'POST':
    almacen = Almacen.objects.get(pk = request.POST.get('almacen'))
    quien = request.user
    fecha = request.POST.get('fecha')
    monto = request.POST.get('monto')
    razon = request.POST.get('razon')
    tipo = TipoGasto.objects.get(pk = request.POST.get('tipo'))

    gasto = Gasto(almacen = almacen, quien = quien, fecha = fecha, monto = monto, razon = razon, tipo = tipo)
    gasto.save()

    messages.success(request, 'Se ha guardado el gasto.')
    return HttpResponseRedirect(reverse('gastos'))

  almacenes = Almacen.objects.all()
  gastos = TipoGasto.objects.all()
  context = {'almacenes': almacenes, 'tipos': gastos}
  return render_to_response('gasto-nuevo.html', context, context_instance = RequestContext(request))

@login_required
def gasto_view(request, id):
  gasto = Gasto.objects.get(pk = id)
  context = {'gasto': gasto}
  return render_to_response('gasto-ver.html', context, context_instance = RequestContext(request))

# Core
@login_required
def clientes(request):
  clientes = Cliente.objects.all()
  context = {'clientes': clientes}
  return render_to_response('clientes.html', context, context_instance = RequestContext(request))

@login_required
def proveedores(request):
  proveedores = Proveedor.objects.all()
  context = {'proveedores': proveedores}
  return render_to_response('proveedores.html', context, context_instance = RequestContext(request))

@login_required
def inventario(request):
  stock = Stock.objects.all()
  almacenes = Almacen.objects.all()
  context = {'stock': stock, 'almacenes': almacenes}
  return render_to_response('inventario.html', context, context_instance = RequestContext(request))

@login_required
def inventario_print(request, id):
  almacen = Almacen.objects.get(pk = id)
  stock = Stock.objects.filter(en_almacen = almacen)
  resp = HttpResponse(content_type = 'application/pdf')
  context = {'stock': stock, 'almacen': almacen, 'total': total_monto_stock(almacen), 'total_real': total_monto_stock_real(almacen)}
  result = generate_pdf('pdf/inventario.html', file_object = resp, context = context)
  return result

# Liquidación
@login_required
def liquidacion(request):
  context = {}
  if request.method == 'POST':

    almacen = Almacen.objects.get(pk = request.POST.get('almacen'))
    fecha = request.POST.get('fecha')
    if request.POST.get('user'):
      userid = request.POST.get('user')
      quien = User.objects.get(pk = userid)
    else:
      quien = request.user

    context['method'] = 'post'
    context['almacen'] = almacen
    context['fecha'] = fecha
    context['quien'] = quien

    gastos = Gasto.objects.filter(almacen = almacen, fecha = fecha, quien = quien)
    contados = Venta.objects.filter(almacen = almacen, fecha_factura = fecha, vendedor = quien, tipo_venta = 'C')
    amortizaciones = Amortizacion.objects.filter(deuda__registro_padre__almacen = almacen, fecha = fecha, recibido_por = quien)
    amortizaciones = amortizaciones.filter(~Q(monto = 0))

    context['gastos'] = gastos
    context['contados'] = contados
    context['amortizaciones'] = amortizaciones

    monto_gastos = total_gastos(gastos)
    monto_contados = total_contados(contados)
    monto_amortizaciones = total_amortizacion(amortizaciones)
    monto_liquidacion = total_liquidacion(monto_gastos, monto_contados, monto_amortizaciones)

    context['monto_gastos'] = monto_gastos
    context['monto_contados'] = monto_contados
    context['monto_amortizaciones'] = monto_amortizaciones
    context['monto_liquidacion'] = monto_liquidacion


  almacenes = Almacen.objects.all()
  context['almacenes'] = almacenes
  context['users'] = User.objects.filter(id__gt = 1)
  return render_to_response('liquidacion.html', context, context_instance = RequestContext(request))

@login_required
def liquidacion_print(request, fecha, id, user):
  context = {}

  almacen = Almacen.objects.get(pk = id)
  quien = User.objects.get(pk = user)

  context['almacen'] = almacen
  context['fecha'] = fecha
  context['quien'] = quien

  gastos = Gasto.objects.filter(almacen = almacen, fecha = fecha, quien = quien)
  contados = Venta.objects.filter(almacen = almacen, fecha_factura = fecha, vendedor = quien, tipo_venta = 'C')
  amortizaciones = Amortizacion.objects.filter(deuda__registro_padre__almacen = almacen, fecha = fecha, recibido_por = quien)
  amortizaciones = amortizaciones.filter(~Q(monto = 0))

  context['gastos'] = gastos
  context['contados'] = contados
  context['amortizaciones'] = amortizaciones

  monto_gastos = total_gastos(gastos)
  monto_contados = total_contados(contados)
  monto_amortizaciones = total_amortizacion(amortizaciones)
  monto_liquidacion = total_liquidacion(monto_gastos, monto_contados, monto_amortizaciones)

  context['monto_gastos'] = monto_gastos
  context['monto_contados'] = monto_contados
  context['monto_amortizaciones'] = monto_amortizaciones
  context['monto_liquidacion'] = monto_liquidacion
    


  almacenes = Almacen.objects.all()
  context['almacenes'] = almacenes

  resp = HttpResponse(content_type = 'application/pdf')
  result = generate_pdf('pdf/liquidacion.html', file_object = resp, context = context)
  return result

@login_required
def index(request):
  return render_to_response('index.html', context_instance = RequestContext(request))

def the_login(request):
  if(request.user.is_authenticated()):
    return HttpResponseRedirect(reverse('index'))
  else:
    if request.method == 'POST':
      username = request.POST['username']
      password = request.POST['password']

      user = authenticate(username = username, password = password)
      if user is not None:
        if user.is_active:
          login(request, user)
          return HttpResponseRedirect(reverse('index'))
        else:
          messages.error(request, 'El usuario no está activo. Contacte con el administrador.')
      else:
        messages.error(request, 'Revise el usuario o la contraseña.')

    usuarios = User.objects.filter(is_active = True)
    context = {'usuarios': usuarios}
  
  return render_to_response('login.html', context, context_instance = RequestContext(request))

def the_logout(request):
  messages.success(request, 'Hasta pronto')
  logout(request)

  return HttpResponseRedirect(reverse('index'))


@login_required
def cotizacion(request):
  if request.method == 'POST':
    cotizacion_form = CotizacionForm(request.POST)
    detalle_form = CotizacionDetalleFormSet(request.POST)

    if cotizacion_form.is_valid() and detalle_form.is_valid():
      instance = cotizacion_form.save()
      detalle_form.instance = instance
      detalle_form.save()

      messages.success(request, 'Se ha guardado la cotización.')

      return HttpResponseRedirect(reverse('cotizaciones'))

  almacenes = Almacen.objects.all()
  context = {'detalle_form': CotizacionDetalleFormSet, 'almacenes': almacenes}
  return render_to_response('cotizacion-nuevo.html', context, context_instance = RequestContext(request))

@login_required
def cotizaciones(request):
  cotizaciones = Cotizacion.objects.all().order_by('-id')
  context = {'cotizaciones': cotizaciones}
  return render_to_response('cotizaciones.html', context, context_instance = RequestContext(request))

@login_required
def cotizacion_view(request, id):
  cotizacion = Cotizacion.objects.get(pk = id)
  context = {'cotizacion': cotizacion}
  return render_to_response('cotizacion-ver.html', context, context_instance = RequestContext(request))

@login_required
def cotizacion_print(request, id):
  cotizacion = Cotizacion.objects.get(id = id)

  resp = HttpResponse(content_type = 'application/pdf')
  context = {'cotizacion': cotizacion}
  result = generate_pdf('pdf/cotizacion.html', file_object = resp, context = context)
  return result

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
@login_required
def producto(request):
  producto_form = ProductoForm(request.POST)

  if producto_form.is_valid():
    instance = producto_form.save()
    instance.activo = True
    instance.precio_costo = instance.precio_costo * Decimal(1.18)
    instance.save()

    lote = Lote(producto = instance, numero = request.POST.get('numero'), vencimiento = request.POST.get('vencimiento'))
    lote.save()
    
    return HttpResponse('1')

@csrf_exempt
@login_required
def producto_lote(request):
  instance = Producto.objects.get(pk = request.POST.get('producto-id'))

  lote = Lote(producto = instance, numero = request.POST.get('numero'), vencimiento = request.POST.get('vencimiento'))
  lote.save()
  
  return HttpResponse('1')

@csrf_exempt
@login_required
def venta_editar(request):
  pk = request.POST.get('pk')
  name = request.POST.get('name')
  value = request.POST.get('value')
  
  venta = Venta.objects.get(pk = pk)
  setattr(venta, name, value)
  venta.save()

  return HttpResponse('1')
