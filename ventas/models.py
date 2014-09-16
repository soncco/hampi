# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from decimal import *

class Venta(models.Model):
  DOCUMENTOS = (
    ('B', 'Boleta'),
    ('F', 'Factura'),
  )
  TIPOS = (
    ('P', 'Crédito'),
    ('C', 'Contado'),
  )
  almacen = models.ForeignKey('almacen.Almacen')
  fecha = models.DateField()
  documento = models.CharField(max_length = 1, choices = DOCUMENTOS, default = 'B')
  numero_documento = models.CharField(max_length = 60)
  fecha_documento = models.DateField()
  vendedor = models.ForeignKey(User)
  cliente = models.ForeignKey('core.Cliente')
  total_venta = models.DecimalField(max_digits = 10, decimal_places = 2, default = Decimal('0.00'))
  tipo_venta = models.CharField(max_length = 1, choices = TIPOS, default = 'C')

  def __unicode__(self):
    return "Venta %s" % self.pk

class VentaDetalle(models.Model):
  registro_padre = models.ForeignKey(Venta)
  producto = models.ForeignKey('core.Producto')
  precio_unitario = models.DecimalField(max_digits = 10, decimal_places = 2, default = Decimal('0.00'))
  cantidad = models.IntegerField()
  descuento = models.DecimalField(max_digits = 10, decimal_places = 2, default = Decimal('0.00'))

class Deuda(models.Model):
  ESTADOS = (
    ('D', 'Deuda'),
    ('C', 'Cancelado'),
  )
  registro_padre = models.OneToOneField(Venta)
  total = models.DecimalField(max_digits = 10, decimal_places = 2, default = Decimal('0.00'))
  estado = models.CharField(max_length = 1, choices = ESTADOS, default = 'D')

class Amortizacion(models.Model):
  deuda = models.ForeignKey(Deuda)
  fecha = models.DateField()
  monto = models.DecimalField(max_digits = 10, decimal_places = 2, default = Decimal('0.00'))
  saldo = models.DecimalField(max_digits = 10, decimal_places = 2, default = Decimal('0.00'))
  recibido_por = models.ForeignKey(User)

class Cotizacion(models.Model):
  fecha = models.DateField()
  referencia = models.CharField(max_length = 255)
  quien = models.ForeignKey(User)
  cliente = models.ForeignKey('core.Cliente')
  plazo = models.IntegerField()
  validez = models.IntegerField()
  glosa = models.TextField(blank = True)
  total_cotizacion = models.DecimalField(max_digits = 10, decimal_places = 2, default = Decimal('0.00'))

  class Meta:
    verbose_name = ('Cotización')
    verbose_name_plural = ('Cotizaciones')

class CotizacionDetalle(models.Model):
  registro_padre = models.ForeignKey(Cotizacion)
  producto = models.ForeignKey('core.Producto')
  precio_unitario = models.DecimalField(max_digits = 10, decimal_places = 2, default = Decimal('0.00'))
  cantidad = models.IntegerField()
