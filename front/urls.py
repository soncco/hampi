from django.conf.urls import  include, url

from . import views

urlpatterns = [
  url(r'^$', views.index, name = 'index'),

  url(r'^login/$', views.the_login, name = 'the_login'),
  url(r'^logout/$', views.the_logout, name = 'the_logout'),

  url(r'^venta/$', views.venta, name = 'venta'),
  url(r'^venta/ver/(?P<id>.*)$', views.venta_view, name = 'venta_view'),
  url(r'^ventas/$', views.ventas, name = 'ventas'),
  url(r'^venta/print/(?P<id>.*)$', views.venta_print, name = 'venta_print'),
  url(r'^venta/guia/printx/(?P<id>.*)$', views.venta_guia_print_antiguo, name = 'venta_guia_print_antiguo'),
  url(r'^venta/guia/print/(?P<id>.*)$', views.venta_guia_print, name = 'venta_guia_print'),
  url(r'^venta/factura/printx/(?P<id>.*)$', views.venta_factura_print_antiguo, name = 'venta_factura_print_antiguo'),
  url(r'^venta/factura/print/(?P<id>.*)$', views.venta_factura_print, name = 'venta_factura_print'),
  url(r'^venta/editar/$', views.venta_editar, name = 'venta_editar'),

  url(r'^amortizacion/(?P<id>.*)$', views.amortizacion, name = 'amortizacion'),

  url(r'^deudas/$', views.deudas, name = 'deudas'),

  url(r'^entrada/$', views.entrada, name = 'entrada'),
  url(r'^entrada/ver/(?P<id>.*)$', views.entrada_view, name = 'entrada_view'),
  url(r'^entradas/$', views.entradas, name = 'entradas'),
  url(r'^entrada/print/(?P<id>.*)$', views.entrada_print, name = 'entrada_print'),


  url(r'^salida/$', views.salida, name = 'salida'),
  url(r'^salida/ver/(?P<id>.*)$', views.salida_view, name = 'salida_view'),
  url(r'^salidas/$', views.salidas, name = 'salidas'),
  url(r'^salida/print/(?P<id>.*)$', views.salida_print, name = 'salida_print'),

  url(r'^gasto/$', views.gasto, name = 'gasto'),
  url(r'^gasto/ver/(?P<id>.*)$', views.gasto_view, name = 'gasto_view'),
  url(r'^gastos/$', views.gastos, name = 'gastos'),

  url(r'^clientes/$', views.clientes, name = 'clientes'),
  url(r'^proveedores/$', views.proveedores, name = 'proveedores'),

  url(r'^inventario/$', views.inventario, name = 'inventario'),
  url(r'^inventario/print/(?P<id>.*)$', views.inventario_print, name = 'inventario_print'),

  url(r'^liquidacion/$', views.liquidacion, name = 'liquidacion'),
  url(r'^liquidacion/print/(?P<fecha>.*)/(?P<id>.*)/(?P<user>.*)$', views.liquidacion_print, name = 'liquidacion_print'),

  url(r'^cotizacion/$', views.cotizacion, name = 'cotizacion'),
  url(r'^cotizacion/ver/(?P<id>.*)$', views.cotizacion_view, name = 'cotizacion_view'),
  url(r'^cotizaciones/$', views.cotizaciones, name = 'cotizaciones'),
  url(r'^cotizacion/print/(?P<id>.*)$', views.cotizacion_print, name = 'cotizacion_print'),

  url(r'^producto/agregar$', views.producto, name = 'producto'),
  url(r'^producto/lote/agregar$', views.producto_lote, name = 'producto_lote'),  

]