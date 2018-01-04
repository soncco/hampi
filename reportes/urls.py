from django.conf.urls import include, url

from . import views

urlpatterns = [
  url(r'^excel/deudas/$', views.excel_deudas, name = 'excel_deudas'),
  url(r'^excel/ventas/$', views.excel_ventas, name = 'excel_ventas'),
  url(r'^excel/ranking/$', views.excel_ranking, name = 'excel_ranking'),

  url(r'^excel/entradas/$', views.excel_entradas, name = 'excel_entradas'),
  url(r'^excel/salidas/$', views.excel_salidas, name = 'excel_salidas'),

  url(r'^excel/gastos/$', views.excel_gastos, name = 'excel_gastos'),

  url(r'^excel/inventario/$', views.excel_inventario, name = 'excel_inventario'),
  url(r'^excel/clientes/$', views.excel_clientes, name = 'excel_clientes'),
  url(r'^excel/proveedores/$', views.excel_proveedores, name = 'excel_proveedores'),

  url(r'^excel/cotizaciones/$', views.excel_cotizaciones, name = 'excel_cotizaciones'),

  url(r'^anexo/print/(?P<id>.*)$', views.anexo_print, name = 'anexo_print'),
  url(r'^kardex/(?P<id>.*)$', views.kardex_excel, name = 'kardex_excel'),
  url(r'^kardex2/(?P<id>.*)$', views.kardex2_excel, name = 'kardex2_excel'),
  url(r'^anexo/pdf/print/(?P<id>.*)$', views.anexo_pdf_print, name = 'anexo_pdf_print'),

  url(r'^vendidos/$', views.vendidos, name = 'vendidos'),
  url(r'^excel/vendidos/$', views.excel_vendidos, name = 'excel_vendidos'),
  url(r'^excel/vendidos/fecha/$', views.excel_vendidos_fecha, name = 'excel_vendidos_fecha'),
]