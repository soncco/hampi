from django.contrib import admin

from models import Venta, VentaDetalle, Deuda, Amortizacion

class VentaDetalleInline(admin.TabularInline):
  model = VentaDetalle

class AmortizacionInline(admin.TabularInline):
  model = Amortizacion

class VentaAdmin(admin.ModelAdmin):
  list_display = ('id', 'fecha', 'documento', 'numero_documento', 'vendedor', 'cliente', 'total_venta',)
  list_filter = ('vendedor__first_name', 'fecha', 'cliente',)
  inlines = [VentaDetalleInline,]

class DeudaAdmin(admin.ModelAdmin):
  list_display = ('registro_padre', 'total', 'estado',)
  inlines = [AmortizacionInline,]

admin.site.register(Venta, VentaAdmin)
admin.site.register(Deuda, DeudaAdmin)
