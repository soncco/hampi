from models import Almacen, Stock
from rest_framework import serializers
from core.serializers import ProductoAlmacenSerializer

class AlmacenSerializer(serializers.HyperlinkedModelSerializer):
  class Meta:
    model = Almacen
    fields = ('url', 'id', 'nombre',)

class StockSerializer(serializers.HyperlinkedModelSerializer):
  producto =  ProductoAlmacenSerializer()
  class Meta:
    model = Stock
    fields = ('producto', 'unidades',)
