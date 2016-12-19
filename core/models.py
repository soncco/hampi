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
  precio_unidad = models.DecimalField(max_digits = 19, decimal_places = 6, default = Decimal('0.000000'))
  activo = models.BooleanField(default = True)

  def __unicode__(self):
    return self.producto

class Lote(models.Model):
  numero = models.CharField(max_length = 255, blank = True)
  vencimiento = models.DateField(blank = True, null = True)
  producto = models.ForeignKey(Producto)
  precio_costo = models.DecimalField(max_digits = 19, decimal_places = 6, default = Decimal('0.000000'))
  nrs = models.CharField(max_length = 255, blank = True, null = True)
  vrs = models.CharField(max_length = 255, blank = True, null = True)

  def __unicode__(self):
    return '%s - Lote: %s' % (self.producto.producto, self.numero)

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
  codcliente = models.CharField(max_length = 255, blank = True)
  razon_social = models.CharField(max_length = 255)
  tipo_documento = models.CharField(max_length = 1, choices = TIPOS, default = 'R')
  numero_documento  = models.CharField(max_length = 60)
  direccion = models.CharField(max_length = 255, blank = True)
  ciudad = models.CharField("Distrito", max_length = 100, blank = True)
  distrito = models.CharField("Provincia", max_length = 100, blank = True)
  departamento = models.CharField("Departamento", max_length = 100, blank = True)
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
