from django.conf.urls import patterns, include, url

urlpatterns = patterns('reportes.views',
  url(r'^excel/deudas/$', 'excel_deudas', name = 'excel_deudas'),
  url(r'^excel/ventas/$', 'excel_ventas', name = 'excel_ventas'),
  url(r'^excel/ranking/$', 'excel_ranking', name = 'excel_ranking'),

  url(r'^excel/entradas/$', 'excel_entradas', name = 'excel_entradas'),
  url(r'^excel/salidas/$', 'excel_salidas', name = 'excel_salidas'),

  url(r'^excel/gastos/$', 'excel_gastos', name = 'excel_gastos'),

  url(r'^excel/inventario/$', 'excel_inventario', name = 'excel_inventario'),
  url(r'^excel/clientes/$', 'excel_clientes', name = 'excel_clientes'),
  url(r'^excel/proveedores/$', 'excel_proveedores', name = 'excel_proveedores'),

  url(r'^excel/cotizaciones/$', 'excel_cotizaciones', name = 'excel_cotizaciones'),

  url(r'^anexo/print/(?P<id>.*)$', 'anexo_print', name = 'anexo_print'),
)