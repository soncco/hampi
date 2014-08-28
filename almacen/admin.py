# -*- coding: utf-8 -*-

from django.contrib import admin

from models import Almacen, Stock, Entrada, EntradaDetalle, Salida, SalidaDetalle

class StockAdmin(admin.ModelAdmin):
  list_display = ('en_almacen', 'codigo', 'producto', 'unidades',)
  list_filter = ('en_almacen',)
  search_fields = ['producto__codigo', 'producto__producto']

  def codigo(self, obj):
    return "%s" % (obj.producto.codigo)
  codigo.short_description = "Código"

class EntradaDetalleInline(admin.TabularInline):
  model = EntradaDetalle

class SalidaDetalleInline(admin.TabularInline):
  model = SalidaDetalle

class EntradaAdmin(admin.ModelAdmin):
  list_display = ('fecha', 'documento', 'numero_documento', 'quien', 'almacen',)
  list_filter = ('quien__first_name', 'fecha', 'almacen',)
  inlines = [EntradaDetalleInline,]

class SalidaAdmin(admin.ModelAdmin):
  list_display = ('fecha', 'documento', 'numero_documento', 'quien', 'almacen')
  list_filter = ('quien__first_name', 'fecha', 'almacen',)
  inlines = [SalidaDetalleInline,]

admin.site.register(Almacen)
admin.site.register(Stock, StockAdmin)
admin.site.register(Entrada, EntradaAdmin)
admin.site.register(Salida, SalidaAdmin)
