# -*- coding: utf-8 -*-

from django.shortcuts import render

from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test

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
from almacen.utils import devolver_stock

from core.models import Gasto, Cliente, Proveedor, TipoGasto, Lote, Producto
from core.forms import ProductoForm

from .utils import total_gastos, total_contados, total_amortizacion, total_liquidacion, diff_dates, grupo_administracion

from io import BytesIO

# Ventas
@login_required
@user_passes_test(grupo_administracion)
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
      print venta_form.errors
      print detalle_form.errors

  almacenes = Almacen.objects.all()
  context = {'detalle_form': DetalleFormSet, 'almacenes': almacenes}
  return render(request, 'front/venta-nuevo.html', context)

@login_required
def ventas(request):
  ventas = Venta.objects.all().order_by('-id')
  for venta in ventas:
    try:
      venta.saldo = saldo_deuda(venta.deuda)
    except:
      venta.saldo = 'Sin deuda'
  context = {'ventas': ventas}
  return render(request, 'front/ventas.html', context)

@login_required
def venta_view(request, id):
  venta = Venta.objects.get(pk = id)
  context = {'venta': venta}
  if venta.tipo_venta == 'P':
    amortizaciones = Amortizacion.objects.filter(deuda = venta.deuda.pk)
    context['amortizaciones'] = amortizaciones
  return render(request, 'front/venta-ver.html', context)

@login_required
def venta_print(request, id):
  venta = Venta.objects.get(id = id)

  resp = HttpResponse(content_type = 'application/pdf')
  context = {'venta': venta}
  if venta.tipo_venta == 'P':
    amortizaciones = Amortizacion.objects.filter(deuda = venta.deuda.pk)
    context['amortizaciones'] = amortizaciones
  result = generate_pdf('front/pdf/venta.html', file_object = resp, context = context)
  return result

@login_required
def venta_delete(request, id):
  venta = Venta.objects.get(pk = id)
  pk = venta.pk
  devolver_stock(venta)
  venta.delete()
  messages.success(request, 'Se ha borrado la venta %s, también se ha restaurado el stock.' % pk)
  return HttpResponseRedirect(reverse('ventas'))


@login_required
def deudas(request):
  deudas = Deuda.objects.all().order_by('-id')
  for deuda in deudas:
    deuda.atrasado = diff_dates(deuda.registro_padre.fecha_factura, date.today())
    deuda.saldo = saldo_deuda(deuda)

  context = {'deudas': deudas}
  return render(request, 'front/deudas.html', context)

@login_required
@user_passes_test(grupo_administracion)
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
  return render(request, 'front/amortizacion.html', context)

# Entradas
@login_required
def entradas(request):
  entradas = Entrada.objects.all().order_by('-id')
  context = {'entradas': entradas}
  return render(request, 'front/entradas.html', context)

@login_required
@user_passes_test(grupo_administracion)
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
  return render(request, 'front/entrada-nuevo.html', context)

@login_required
def entrada_view(request, id):
  entrada = Entrada.objects.get(pk = id)
  context = {'entrada': entrada}
  return render(request, 'front/entrada-ver.html', context)

@login_required
def entrada_print(request, id):
  entrada = Entrada.objects.get(id = id)

  resp = HttpResponse(content_type = 'application/pdf')
  context = {'entrada': entrada}
  result = generate_pdf('front/pdf/entrada.html', file_object = resp, context = context)
  return result

# Salidas
@login_required
def salidas(request):
  salidas = Salida.objects.all().order_by('-id')
  context = {'salidas': salidas}
  return render(request, 'front/salidas.html', context)

@login_required
@user_passes_test(grupo_administracion)
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
  return render(request, 'front/salida-nuevo.html', context)

@login_required
def salida_view(request, id):
  salida = Salida.objects.get(pk = id)
  context = {'salida': salida}
  return render(request, 'front/salida-ver.html', context)

@login_required
def salida_print(request, id):
  salida = Salida.objects.get(id = id)

  resp = HttpResponse(content_type = 'application/pdf')
  context = {'salida': salida}
  result = generate_pdf('front/pdf/salida.html', file_object = resp, context = context)
  return result

# Gastos
@login_required
def gastos(request):
  gastos = Gasto.objects.all().order_by('-id')
  context = {'gastos': gastos}
  return render(request, 'front/gastos.html', context)

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
  return render(request, 'front/gasto-nuevo.html', context)

@login_required
def gasto_view(request, id):
  gasto = Gasto.objects.get(pk = id)
  context = {'gasto': gasto}
  return render(request, 'front/gasto-ver.html', context)

# Core
@login_required
def clientes(request):
  clientes = Cliente.objects.all()
  context = {'clientes': clientes}
  return render(request, 'front/clientes.html', context)

@login_required
def proveedores(request):
  proveedores = Proveedor.objects.all()
  context = {'proveedores': proveedores}
  return render(request, 'front/proveedores.html', context)

@login_required
def inventario(request):
  stock = Stock.objects.all()
  almacenes = Almacen.objects.all()
  context = {'stock': stock, 'almacenes': almacenes}
  return render(request, 'front/inventario.html', context)

@login_required
def inventario_print(request, id):
  almacen = Almacen.objects.get(pk = id)
  stock = Stock.objects.filter(en_almacen = almacen)
  resp = HttpResponse(content_type = 'application/pdf')
  context = {'stock': stock, 'almacen': almacen, 'total': total_monto_stock(almacen), 'total_real': total_monto_stock_real(almacen)}
  result = generate_pdf('front/pdf/inventario.html', file_object = resp, context = context)
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
  return render(request, 'front/liquidacion.html', context)

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
  result = generate_pdf('front/pdf/liquidacion.html', file_object = resp, context = context)
  return result

@login_required
def index(request):
  return render(request, 'front/index.html')

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
  
  return render(request, 'front/login.html', context)

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
  return render(request, 'front/cotizacion-nuevo.html', context)

@login_required
def cotizaciones(request):
  cotizaciones = Cotizacion.objects.all().order_by('-id')
  context = {'cotizaciones': cotizaciones}
  return render(request, 'front/cotizaciones.html', context)

@login_required
def cotizacion_view(request, id):
  cotizacion = Cotizacion.objects.get(pk = id)
  context = {'cotizacion': cotizacion}
  return render(request, 'front/cotizacion-ver.html', context)

@login_required
def historial(request, id):
  p = Producto.objects.get(pk = id)
  productos = Producto.objects.filter(producto = p.producto)

  context = {'productos': productos, 'producto': p}
  return render(request, 'front/historial.html', context)

@login_required
def cotizacion_print(request, id):
  cotizacion = Cotizacion.objects.get(id = id)

  resp = HttpResponse(content_type = 'application/pdf')
  context = {'cotizacion': cotizacion}
  result = generate_pdf('front/pdf/cotizacion.html', file_object = resp, context = context)
  return result

from reportes.views import excel_vendidos_fecha, excel_proveedores_fecha, excel_clientes_fecha
@login_required
def varios(request):
  if request.method == 'POST':
    tipo = request.POST.get('tipo')
    if tipo == 'productos':
      return excel_vendidos_fecha(request)
    elif tipo == 'proveedores':
      return excel_proveedores_fecha(request)
    elif tipo == 'clientes':
      return excel_clientes_fecha(request)

    return HttpResponse('test')
  return render(request, 'front/informes-varios.html')

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
@login_required
def producto(request):
  producto_form = ProductoForm(request.POST)

  if producto_form.is_valid():
    instance = producto_form.save()
    instance.activo = True
    instance.save()

    if request.POST.get('vencimiento') == '':
      lote = Lote(producto = instance, numero = request.POST.get('numero'), nrs = request.POST.get('nrs'), vrs = request.POST.get('vrs'), precio_costo = request.POST.get('precio_costo'))
    else:
      lote = Lote(producto = instance, numero = request.POST.get('numero'), vencimiento = request.POST.get('vencimiento'), nrs = request.POST.get('nrs'), vrs = request.POST.get('vrs'), precio_costo = request.POST.get('precio_costo'))
    lote.save()
    
    return HttpResponse('1')

@csrf_exempt
@login_required
def producto_lote(request):
  instance = Producto.objects.get(pk = request.POST.get('producto-id'))
  if request.POST.get('vencimiento') == '':
    lote = Lote(producto = instance, numero = request.POST.get('numero'), nrs = request.POST.get('nrs'), vrs = request.POST.get('vrs'), precio_costo = request.POST.get('precio_costo'))
  else:
    lote = Lote(producto = instance, numero = request.POST.get('numero'), vencimiento = request.POST.get('vencimiento'), nrs = request.POST.get('nrs'), vrs = request.POST.get('vrs'), precio_costo = request.POST.get('precio_costo'))
  lote.save()
  
  return HttpResponse('1')

@csrf_exempt
@login_required
@user_passes_test(grupo_administracion)
def venta_editar(request):
  pk = request.POST.get('pk')
  name = request.POST.get('name')
  value = request.POST.get('value')
  
  venta = Venta.objects.get(pk = pk)
  setattr(venta, name, value)
  venta.save()

  return HttpResponse('1')

from printable import ImpresionFactura
@login_required
def venta_factura_print(request, id):
  venta = Venta.objects.get(id = id)

  response = HttpResponse(content_type='application/pdf')

  buffer = BytesIO()

  report = ImpresionFactura(buffer, 'A4')
  pdf = report.imprimir(venta)

  response.write(pdf)
  return response

from printable import ImpresionGuia
@login_required
def venta_guia_print(request, id):
  venta = Venta.objects.get(id = id)

  response = HttpResponse(content_type='application/pdf')

  buffer = BytesIO()

  report = ImpresionGuia(buffer, 'A4')
  pdf = report.imprimir(venta)

  response.write(pdf)
  return response
