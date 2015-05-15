from django.conf.urls import patterns, include, url

urlpatterns = patterns('front.views',
  url(r'^$', 'index', name = 'index'),

  url(r'^login/$', 'the_login', name = 'the_login'),
  url(r'^logout/$', 'the_logout', name = 'the_logout'),

  url(r'^venta/$', 'venta', name = 'venta'),
  url(r'^venta/ver/(?P<id>.*)$', 'venta_view', name = 'venta_view'),
  url(r'^ventas/$', 'ventas', name = 'ventas'),
  url(r'^venta/print/(?P<id>.*)$', 'venta_print', name = 'venta_print'),
  url(r'^venta/guia/print/(?P<id>.*)$', 'venta_guia_print', name = 'venta_guia_print'),
  url(r'^venta/factura/print/(?P<id>.*)$', 'venta_factura_print', name = 'venta_factura_print'),
  url(r'^venta/editar/$', 'venta_editar', name = 'venta_editar'),

  url(r'^amortizacion/(?P<id>.*)$', 'amortizacion', name = 'amortizacion'),

  url(r'^deudas/$', 'deudas', name = 'deudas'),

  url(r'^entrada/$', 'entrada', name = 'entrada'),
  url(r'^entrada/ver/(?P<id>.*)$', 'entrada_view', name = 'entrada_view'),
  url(r'^entradas/$', 'entradas', name = 'entradas'),
  url(r'^entrada/print/(?P<id>.*)$', 'entrada_print', name = 'entrada_print'),


  url(r'^salida/$', 'salida', name = 'salida'),
  url(r'^salida/ver/(?P<id>.*)$', 'salida_view', name = 'salida_view'),
  url(r'^salidas/$', 'salidas', name = 'salidas'),
  url(r'^salida/print/(?P<id>.*)$', 'salida_print', name = 'salida_print'),

  url(r'^gasto/$', 'gasto', name = 'gasto'),
  url(r'^gasto/ver/(?P<id>.*)$', 'gasto_view', name = 'gasto_view'),
  url(r'^gastos/$', 'gastos', name = 'gastos'),

  url(r'^clientes/$', 'clientes', name = 'clientes'),
  url(r'^proveedores/$', 'proveedores', name = 'proveedores'),

  url(r'^inventario/$', 'inventario', name = 'inventario'),
  url(r'^inventario/print/(?P<id>.*)$', 'inventario_print', name = 'inventario_print'),

  url(r'^liquidacion/$', 'liquidacion', name = 'liquidacion'),
  url(r'^liquidacion/print/(?P<fecha>.*)/(?P<id>.*)/(?P<user>.*)$', 'liquidacion_print', name = 'liquidacion_print'),

  url(r'^cotizacion/$', 'cotizacion', name = 'cotizacion'),
  url(r'^cotizacion/ver/(?P<id>.*)$', 'cotizacion_view', name = 'cotizacion_view'),
  url(r'^cotizaciones/$', 'cotizaciones', name = 'cotizaciones'),
  url(r'^cotizacion/print/(?P<id>.*)$', 'cotizacion_print', name = 'cotizacion_print'),

  url(r'^producto/agregar$', 'producto', name = 'producto'),
  url(r'^producto/lote/agregar$', 'producto_lote', name = 'producto_lote'),  

)
