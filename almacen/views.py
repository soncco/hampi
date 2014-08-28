from django.shortcuts import render

# Rest API
from rest_framework import viewsets, generics
from serializers import AlmacenSerializer, StockSerializer

from models import Almacen, Stock

class AlmacenViewSet(viewsets.ModelViewSet):
  queryset = Almacen.objects.all()
  serializer_class = AlmacenSerializer

class StockViewSet(viewsets.ModelViewSet):
  queryset = Stock.objects.all()
  serializer_class = StockSerializer

class StockAlmacenFilterList(generics.ListAPIView):
  serializer_class = StockSerializer

  def get_queryset(self):
    almacen = self.request.QUERY_PARAMS.get('almacen', None)
    term = self.request.QUERY_PARAMS.get('term', None)
    queryset = Stock.objects.filter(en_almacen = almacen, unidades__gt = 0)

    if term is not None:
      queryset = queryset.filter(producto__producto__icontains = term) | queryset.filter(producto__codigo__icontains = term)

    return queryset
