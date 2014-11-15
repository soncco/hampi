from models import Almacen, Stock
from rest_framework import serializers
from core.serializers import LoteAlmacenSerializer

class AlmacenSerializer(serializers.HyperlinkedModelSerializer):
  class Meta:
    model = Almacen
    fields = ('url', 'id', 'nombre',)

class StockSerializer(serializers.HyperlinkedModelSerializer):
  lote =  LoteAlmacenSerializer()
  class Meta:
    model = Stock
    fields = ('lote', 'unidades',)
