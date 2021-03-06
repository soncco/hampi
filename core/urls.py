from django.conf.urls import include, url

from rest_framework import routers
from views import ProductoViewSet, ProductoFilterList, ClienteViewSet, ClienteFilterList, ProveedorViewSet, ProveedorFilterList, LoteViewSet, LoteFilterList

router = routers.DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'lotes', LoteViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'proveedores', ProveedorViewSet)

urlpatterns = [
  # Rest API
  url(r'^api/core/', include(router.urls)),
  url(r'^api/productos-filter/$', ProductoFilterList.as_view()),
  url(r'^api/lotes-filter/$', LoteFilterList.as_view()),
  url(r'^api/clientes-filter/$', ClienteFilterList.as_view()),
  url(r'^api/proveedores-filter/$', ProveedorFilterList.as_view()),
]