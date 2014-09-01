from models import Producto, Cliente, Proveedor
from rest_framework import serializers

class ProductoSerializer(serializers.HyperlinkedModelSerializer):
  class Meta:
    model = Producto
    fields = ('url', 'id', 'codigo', 'unidad_caja', 'producto', 'precio_unidad', 'precio_caja', 'precio_costo', 'activo')

class ProductoAlmacenSerializer(serializers.ModelSerializer):
  class Meta(object):
    model = Producto
    fields = ('id', 'codigo', 'unidad_caja', 'producto', 'precio_unidad', 'precio_caja', 'precio_costo', 'activo')      

class ClienteSerializer(serializers.HyperlinkedModelSerializer):
  class Meta:
    model = Cliente
    fields = ('url', 'id', 'razon_social', 'numero_documento',)

class ProveedorSerializer(serializers.HyperlinkedModelSerializer):
  class Meta:
    model = Proveedor
    fields = ('url', 'id', 'razon_social', 'ruc', 'direccion',)
