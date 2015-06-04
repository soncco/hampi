# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from decimal import *

class Almacen(models.Model):
  nombre = models.CharField(max_length = 100)

  class Meta:
    verbose_name = ('Almacén')
    verbose_name_plural = ('Almacenes')

  def __unicode__(self):
    return self.nombre

class Stock(models.Model):
  en_almacen = models.ForeignKey(Almacen)
  lote = models.ForeignKey('core.Lote')
  unidades = models.IntegerField()

class Entrada(models.Model):
  fecha = models.DateField()
  numero_factura = models.CharField(max_length = 60)
  fecha_factura = models.DateField()
  numero_guia = models.CharField(max_length = 60)
  fecha_guia = models.DateField()
  almacen = models.ForeignKey(Almacen)
  notas = models.TextField(blank = True)
  proveedor = models.ForeignKey('core.Proveedor', blank = True, null = True)
  quien = models.ForeignKey(User)
  fecha_entrada = models.DateField(null = True, blank = True)
  hora_entrada = models.CharField(max_length = 20, blank = True, null = True)

class EntradaDetalle(models.Model):
  entrada_padre = models.ForeignKey(Entrada)
  lote = models.ForeignKey('core.Lote')
  precio_unitario = models.DecimalField(max_digits = 19, decimal_places = 6, default = Decimal('0.000000'))
  cantidad = models.IntegerField()
  total = models.DecimalField(max_digits = 19, decimal_places = 6, default = Decimal('0.000000'))

class Salida(models.Model):
  fecha = models.DateField()
  numero_factura = models.CharField(max_length = 60)
  fecha_factura = models.DateField()
  numero_guia = models.CharField(max_length = 60)
  fecha_guia = models.DateField()
  almacen = models.ForeignKey(Almacen)
  notas = models.TextField(blank = True)
  quien = models.ForeignKey(User)
  venta = models.ForeignKey('ventas.Venta', blank = True, null = True)

class SalidaDetalle(models.Model):
  salida_padre = models.ForeignKey(Salida)
  lote = models.ForeignKey('core.Lote')
  precio_unitario = models.DecimalField(max_digits = 19, decimal_places = 6, default = Decimal('0.000000'))
  cantidad = models.IntegerField()
  total = models.DecimalField(max_digits = 19, decimal_places = 6, default = Decimal('0.000000'))
