from django.shortcuts import render

# Rest API
from rest_framework import viewsets, generics
from serializers import ProductoSerializer, ClienteSerializer, ProveedorSerializer, LoteSerializer

from models import Producto, Cliente, Proveedor, Lote

class ProductoViewSet(viewsets.ModelViewSet):
  queryset = Producto.objects.filter(activo = True)
  serializer_class = ProductoSerializer

class LoteViewSet(viewsets.ModelViewSet):
  queryset = Lote.objects.filter(producto__activo = True)
  serializer_class = LoteSerializer

class ProductoFilterList(generics.ListAPIView):
  serializer_class = ProductoSerializer

  def get_queryset(self):
    queryset = Producto.objects.filter(activo = True)
    term = self.request.QUERY_PARAMS.get('term', None)

    if term is not None:
      queryset = queryset.filter(producto__icontains = term) | queryset.filter(codigo__icontains = term) | queryset.filter(marca__icontains = term) | queryset.filter(comercial__icontains = term)

    return queryset

class LoteFilterList(generics.ListAPIView):
  serializer_class = LoteSerializer

  def get_queryset(self):
    queryset = Lote.objects.filter(producto__activo = True)
    term = self.request.QUERY_PARAMS.get('term', None)

    if term is not None:
      queryset = queryset.filter(producto__producto__icontains = term) | queryset.filter(producto__codigo__icontains = term) | queryset.filter(numero__icontains = term) | queryset.filter(producto__codigo__icontains = term) |  queryset.filter(producto__marca__icontains = term) |  queryset.filter(producto__comercial__icontains = term)

    return queryset

class ClienteViewSet(viewsets.ModelViewSet):
  queryset = Cliente.objects.all()
  serializer_class = ClienteSerializer

class ClienteFilterList(generics.ListAPIView):
  serializer_class = ClienteSerializer

  def get_queryset(self):
    queryset = Cliente.objects.all()
    term = self.request.QUERY_PARAMS.get('term', None)

    if term is not None:
      queryset = queryset.filter(razon_social__icontains = term) | queryset.filter(numero_documento__icontains = term)

    return queryset

class ProveedorViewSet(viewsets.ModelViewSet):
  queryset = Proveedor.objects.all()
  serializer_class = ProveedorSerializer

class ProveedorFilterList(generics.ListAPIView):
  serializer_class = ProveedorSerializer

  def get_queryset(self):
    queryset = Proveedor.objects.all()
    term = self.request.QUERY_PARAMS.get('term', None)

    if term is not None:
      queryset = queryset.filter(razon_social__icontains = term) | queryset.filter(ruc__icontains = term)

    return queryset