# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from decimal import *

class Producto(models.Model):
  codigo = models.CharField(max_length = 255, blank = True)
  producto = models.CharField(max_length = 255)
  marca = models.CharField(max_length = 255)
  comercial = models.CharField(max_length = 255, blank = True)
  unidad_medida = models.CharField(max_length = 100)
  procedencia = models.CharField(max_length = 255, blank = True)
  unidad_caja = models.IntegerField()
  precio_caja = models.DecimalField(max_digits = 10, decimal_places = 2, default = Decimal('0.00'))
  precio_unidad = models.DecimalField(max_digits = 10, decimal_places = 2, default = Decimal('0.00'))
  precio_costo = models.DecimalField(max_digits = 10, decimal_places = 2, default = Decimal('0.00'))
  activo = models.BooleanField(default = True)

  def __unicode__(self):
    return self.producto

class Lote(models.Model):
  numero = models.CharField(max_length = 255)
  vencimiento = models.DateField()
  producto = models.ForeignKey(Producto)

  #def __unicode__(self):
  #  return '%s - Lote: %s %s' (self.producto, self.numero, self.vencimiento)

class Segmento(models.Model):
  nombre = models.CharField(max_length = 100)

  def __unicode__(self):
    return self.nombre  

class Cliente(models.Model):
  TIPOS = (
    ('D', 'DNI'),
    ('R', 'RUC'),
  )
  segmento = models.ForeignKey(Segmento)
  razon_social = models.CharField(max_length = 255)
  tipo_documento = models.CharField(max_length = 1, choices = TIPOS, default = 'R')
  numero_documento  = models.CharField(max_length = 60)
  direccion = models.CharField(max_length = 255, blank = True)
  ciudad = models.CharField(max_length = 100, blank = True)
  distrito = models.CharField(max_length = 100, blank = True)
  telefono = models.CharField(max_length = 50, blank = True)

  def __unicode__(self):
    return self.razon_social

class Proveedor(models.Model):
  razon_social = models.CharField(max_length = 255)
  ruc = models.CharField(max_length = 11)
  direccion = models.CharField(max_length = 100, blank = True)
  ciudad = models.CharField(max_length = 100, blank = True)
  distrito = models.CharField(max_length = 100, blank = True)
  telefono = models.CharField(max_length = 50, blank = True)

  class Meta:
    verbose_name = ('Proveedor')
    verbose_name_plural = ('Proveedores')

  def __unicode__(self):
    return self.razon_social

class TipoGasto(models.Model):
  nombre = models.CharField(max_length = 100)

  class Meta:
    verbose_name = ('Tipo de Gasto')
    verbose_name_plural = ('Tipos de Gasto')

  def __unicode__(self):
    return self.nombre

class Gasto(models.Model):
  almacen = models.ForeignKey('almacen.Almacen')
  quien = models.ForeignKey(User)
  fecha = models.DateField()
  monto = models.DecimalField(max_digits = 10, decimal_places = 2, default = Decimal('0.00'))
  razon = models.TextField()
  tipo = models.ForeignKey(TipoGasto, blank = True, null = True, default = None)
