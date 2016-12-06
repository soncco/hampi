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
    almacen = self.request.query_params.get('almacen', None)
    term = self.request.query_params.get('term', None)
    queryset = Stock.objects.filter(en_almacen = almacen, unidades__gt = 0)

    if term is not None:
      queryset = queryset.filter(lote__producto__producto__icontains = term) | queryset.filter(lote__producto__codigo__icontains = term) | queryset.filter(lote__numero__icontains = term) | queryset.filter(lote__producto__marca__icontains = term) | queryset.filter(lote__producto__comercial__icontains = term)

    return queryset
