from models import Producto, Cliente, Proveedor, Lote
from rest_framework import serializers

class ProductoSerializer(serializers.HyperlinkedModelSerializer):
  class Meta:
    model = Producto
    fields = ('url', 'id', 'codigo', 'comercial', 'producto', 'marca', 'procedencia', 'unidad_medida', 'precio_unidad', 'precio_costo', 'activo',)

class LoteSerializer(serializers.HyperlinkedModelSerializer):
  producto = ProductoSerializer()
  class Meta:
    model = Lote
    fields = ('url', 'id', 'numero', 'vencimiento', 'producto',)

class LoteAlmacenSerializer(serializers.ModelSerializer):
  producto = ProductoSerializer()
  class Meta(object):
    model = Lote
    fields = ('id', 'vencimiento', 'numero', 'producto',)

class ClienteSerializer(serializers.HyperlinkedModelSerializer):
  class Meta:
    model = Cliente
    fields = ('url', 'id', 'razon_social', 'numero_documento', 'direccion', 'ciudad', 'distrito', 'departamento', 'telefono', 'codcliente',)

class ProveedorSerializer(serializers.HyperlinkedModelSerializer):
  class Meta:
    model = Proveedor
    fields = ('url', 'id', 'razon_social', 'ruc', 'direccion',)
