from django.conf.urls import patterns, include, url

from rest_framework import routers
from views import AlmacenViewSet, StockViewSet, StockAlmacenFilterList

router = routers.DefaultRouter()
router.register(r'almacen', AlmacenViewSet)
router.register(r'stock', StockViewSet)

urlpatterns = patterns('almacen.views',
  # Rest API
  url(r'^api/almacen/', include(router.urls)),
  url(r'^api/almacen/stock-filter/$', StockAlmacenFilterList.as_view()),
)