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

from decimal import *
from datetime import date

from ventas.forms import VentaForm, DetalleFormSet, CotizacionForm, CotizacionDetalleFormSet
from ventas.models import Venta, VentaDetalle, Deuda, Amortizacion, Cotizacion, CotizacionDetalle
from ventas.utils import total_amortizaciones, saldo_deuda

from almacen.forms import EntradaForm, EntradaDetalleFormSet, SalidaForm, SalidaDetalleFormSet
from almacen.models import Almacen, Entrada, Salida, Stock
from almacen.utils import generar_salida_venta, entrada_stock, salida_stock, total_monto_stock, total_monto_stock_real

from core.models import Gasto, Cliente, Proveedor, TipoGasto

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

        saldo = instance.total_venta - Decimal(monto)
        deuda = Deuda(registro_padre = instance, total = saldo, estado = 'D')
        deuda.save()

        amortizacion = Amortizacion(deuda = deuda, fecha = instance.fecha, monto = Decimal(monto), saldo = saldo, recibido_por = request.user)
        amortizacion.save()
        messages.success(request, 'Se ha creado también una deuda y una amortización.')
      messages.success(request, 'Se ha guardado la venta y se ha creado una salida.')

      return HttpResponseRedirect(reverse('ventas'))

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
def deudas(request):
  deudas = Deuda.objects.all().order_by('-id')
  for deuda in deudas:
    deuda.atrasado = diff_dates(deuda.registro_padre.fecha_documento, date.today())
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
    contados = Venta.objects.filter(almacen = almacen, fecha_documento = fecha, vendedor = quien, tipo_venta = 'C')
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
  contados = Venta.objects.filter(almacen = almacen, fecha_documento = fecha, vendedor = quien, tipo_venta = 'C')
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