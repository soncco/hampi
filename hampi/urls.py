from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^', include('reportes.urls')),
    url(r'^', include('front.urls')),
    url(r'^', include('core.urls')),
    url(r'^', include('almacen.urls')),
]
