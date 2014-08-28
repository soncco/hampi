from django.shortcuts import render

# Rest API
from rest_framework import viewsets, generics
from serializers import ProductoSerializer, ClienteSerializer, ProveedorSerializer

from models import Producto, Cliente, Proveedor

class ProductoViewSet(viewsets.ModelViewSet):
  queryset = Producto.objects.filter(activo = True)
  serializer_class = ProductoSerializer

class ProductoFilterList(generics.ListAPIView):
  serializer_class = ProductoSerializer

  def get_queryset(self):
    queryset = Producto.objects.filter(activo = True)
    term = self.request.QUERY_PARAMS.get('term', None)

    if term is not None:
      queryset = queryset.filter(producto__icontains = term) | queryset.filter(codigo__icontains = term)

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