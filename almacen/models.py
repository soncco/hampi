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
  producto = models.ForeignKey('core.Producto')
  unidades = models.IntegerField()

class Entrada(models.Model):
  DOCUMENTOS = (
    ('B', 'Boleta'),
    ('F', 'Factura'),
    ('G', 'Guía de Remisión')
  )
  fecha = models.DateField()
  documento = models.CharField(max_length = 1, choices = DOCUMENTOS, default = 'F')
  numero_documento = models.CharField(max_length = 60)
  fecha_documento = models.DateField()
  almacen = models.ForeignKey(Almacen)
  notas = models.TextField(blank = True)
  proveedor = models.ForeignKey('core.Proveedor', blank = True, null = True)
  quien = models.ForeignKey(User)

class EntradaDetalle(models.Model):
  entrada_padre = models.ForeignKey(Entrada)
  producto = models.ForeignKey('core.Producto')
  precio_unitario = models.DecimalField(max_digits = 10, decimal_places = 2, default = Decimal('0.00'))
  cantidad = models.IntegerField()
  descuento = models.DecimalField(max_digits = 10, decimal_places = 2, default = Decimal('0.00'))

class Salida(models.Model):
  DOCUMENTOS = (
    ('B', 'Boleta'),
    ('F', 'Factura'),
    ('G', 'Guía de Remisión')
  )
  fecha = models.DateField()
  documento = models.CharField(max_length = 1, choices = DOCUMENTOS, default = 'F')
  numero_documento = models.CharField(max_length = 60)
  fecha_documento = models.DateField()
  almacen = models.ForeignKey(Almacen)
  notas = models.TextField(blank = True)
  quien = models.ForeignKey(User)
  venta = models.ForeignKey('ventas.Venta', blank = True, null = True)

class SalidaDetalle(models.Model):
  salida_padre = models.ForeignKey(Salida)
  producto = models.ForeignKey('core.Producto')
  precio_unitario = models.DecimalField(max_digits = 10, decimal_places = 2, default = Decimal('0.00'))
  cantidad = models.IntegerField()
  descuento = models.DecimalField(max_digits = 10, decimal_places = 2, default = Decimal('0.00'))
