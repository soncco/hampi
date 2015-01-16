# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from decimal import *

class Venta(models.Model):
  TIPOS = (
    ('P', 'Crédito'),
    ('C', 'Contado'),
  )
  almacen = models.ForeignKey('almacen.Almacen')
  #fecha = models.DateField()
  cliente = models.ForeignKey('core.Cliente')
  vendedor = models.ForeignKey(User)
  total_venta = models.DecimalField(max_digits = 19, decimal_places = 6, default = Decimal('0.000000'))
  tipo_venta = models.CharField(max_length = 1, choices = TIPOS, default = 'C')

  # Factura
  orden_compra = models.CharField(max_length = 100, blank = True)
  numero_factura = models.CharField(max_length = 60)
  fecha_factura = models.DateField()
  condiciones = models.CharField(max_length = 100, blank = True)
  vencimiento = models.DateField(blank = True, null = True)
  zona = models.CharField(max_length = 100, blank = True)
  hora = models.CharField(max_length = 100, blank = True)

  # Guia
  numero_guia = models.CharField(max_length = 60)
  fecha_emision = models.DateField()
  fecha_traslado = models.DateField()
  procedencia = models.CharField(max_length = 255)
  llegada = models.CharField(max_length = 255)
  vehiculo = models.CharField(max_length = 255, blank = True)
  inscripcion = models.CharField(max_length = 255, blank = True)
  licencia = models.CharField(max_length = 100, blank = True)
  costo = models.CharField(max_length = 100, blank = True)
  transportista = models.CharField(max_length = 255, blank = True)
  ruc_transportista = models.CharField(max_length = 11, blank = True)
  bultos = models.CharField(max_length = 100, blank = True)
  despachador = models.CharField(max_length = 100, blank = True)
  jefe_almacen = models.CharField(max_length = 100, blank = True)
  vb = models.CharField(max_length = 100, blank = True)

  def __unicode__(self):
    return "Venta %s" % self.pk

class VentaDetalle(models.Model):
  registro_padre = models.ForeignKey(Venta)
  lote = models.ForeignKey('core.Lote')
  precio_unitario = models.DecimalField(max_digits = 19, decimal_places = 6, default = Decimal('0.000000'))
  cantidad = models.IntegerField()
  total = models.DecimalField(max_digits = 19, decimal_places = 6, default = Decimal('0.000000'))

class Deuda(models.Model):
  ESTADOS = (
    ('D', 'Deuda'),
    ('C', 'Cancelado'),
  )
  registro_padre = models.OneToOneField(Venta)
  total = models.DecimalField(max_digits = 19, decimal_places = 6, default = Decimal('0.000000'))
  estado = models.CharField(max_length = 1, choices = ESTADOS, default = 'D')

class Amortizacion(models.Model):
  deuda = models.ForeignKey(Deuda)
  fecha = models.DateField()
  monto = models.DecimalField(max_digits = 19, decimal_places = 6, default = Decimal('0.000000'))
  saldo = models.DecimalField(max_digits = 19, decimal_places = 6, default = Decimal('0.000000'))
  recibido_por = models.ForeignKey(User)

class Cotizacion(models.Model):
  fecha = models.DateField()
  referencia = models.CharField(max_length = 255)
  quien = models.ForeignKey(User)
  cliente = models.ForeignKey('core.Cliente')
  plazo = models.IntegerField()
  validez = models.IntegerField()
  glosa = models.TextField(blank = True)
  total_cotizacion = models.DecimalField(max_digits = 19, decimal_places = 6, default = Decimal('0.000000'))

  class Meta:
    verbose_name = ('Cotización')
    verbose_name_plural = ('Cotizaciones')

class CotizacionDetalle(models.Model):
  registro_padre = models.ForeignKey(Cotizacion)
  lote = models.ForeignKey('core.Lote')
  precio_unitario = models.DecimalField(max_digits = 19, decimal_places = 6, default = Decimal('0.000000'))
  cantidad = models.IntegerField()
