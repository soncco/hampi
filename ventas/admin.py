from django.contrib import admin

from models import Venta, VentaDetalle, Deuda, Amortizacion, Cotizacion, CotizacionDetalle

class VentaDetalleInline(admin.TabularInline):
  model = VentaDetalle

class AmortizacionInline(admin.TabularInline):
  model = Amortizacion

class CotizacionDetalleInline(admin.TabularInline):
  model = CotizacionDetalle

class VentaAdmin(admin.ModelAdmin):
  list_display = ('id', 'numero_factura', 'numero_guia', 'vendedor', 'cliente', 'total_venta',)
  list_filter = ('vendedor__first_name', 'cliente',)
  inlines = [VentaDetalleInline,]

class DeudaAdmin(admin.ModelAdmin):
  list_display = ('registro_padre', 'total', 'estado',)
  inlines = [AmortizacionInline,]

class CotizacionAdmin(admin.ModelAdmin):
  list_display = ('id', 'fecha', 'referencia', 'quien', 'cliente', 'total_cotizacion',)
  list_filter = ('quien__first_name', 'fecha', 'cliente',)
  inlines = [CotizacionDetalleInline,]

admin.site.register(Venta, VentaAdmin)
admin.site.register(Deuda, DeudaAdmin)
admin.site.register(Cotizacion, CotizacionAdmin)
