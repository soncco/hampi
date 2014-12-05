from django.contrib import admin

from models import Producto, Segmento, Cliente, Proveedor, Gasto, TipoGasto, Lote

class ProductoAdmin(admin.ModelAdmin):
  list_display = ('producto', 'marca', 'procedencia', 'precio_costo', 'precio_unidad', 'activo',)
  list_filter = ('activo', 'marca', 'procedencia',)
  search_fields = ['codigo', 'producto__producto', 'marca', 'procedencia']

class LoteAdmin(admin.ModelAdmin):
  list_display = ('numero', 'vencimiento', 'producto',)
  list_filter = ('vencimiento',)
  search_fields = ['numero']

class ClienteAdmin(admin.ModelAdmin):
  list_display = ('razon_social', 'codcliente', 'tipo_documento', 'numero_documento', 'ciudad', 'distrito', 'departamento',)
  list_filter = ('ciudad', 'distrito', 'departamento', 'segmento',)
  search_fields = ['razon_social', 'numero_documento']

class ProveedorAdmin(admin.ModelAdmin):
  list_display = ('razon_social', 'ruc', 'direccion', 'telefono',)
  search_fields = ['razon_social', 'ruc', 'direccion']

class GastoAdmin(admin.ModelAdmin):
  list_display = ('fecha', 'quien', 'almacen', 'monto', 'tipo',)
  list_filter = ('fecha', 'quien', 'almacen', 'tipo',)

admin.site.register(Segmento)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Lote, LoteAdmin)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Proveedor, ProveedorAdmin)
admin.site.register(Gasto, GastoAdmin)
admin.site.register(TipoGasto)

# Overwrite Admin

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.translation import gettext as _

class MyUserAdmin(UserAdmin):
  def completo(self, obj):
    return "%s %s" % (obj.first_name, obj.last_name)

  def grupos(self, obj):
    gs = ""
    for grupo in obj.groups.all():
      gs += grupo.name + " "

    return gs

  list_display = ('username', 'completo', 'grupos',)
  list_display_links = ('username',)

  fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Staff'), {'fields': ('is_staff',)}),
        (_('Groups'), {'fields': ('groups',)}),
    )

  def queryset(self, request):
    qs = super(MyUserAdmin, self).queryset(request)
    qs = qs.filter(~Q(username = 'brau'))
    return qs

admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
