from django.forms import ModelForm
from django.forms.models import inlineformset_factory

from models import Venta, VentaDetalle, Cotizacion, CotizacionDetalle

class VentaForm(ModelForm):
  class Meta:
    model = Venta
    fields = '__all__'

DetalleFormSet = inlineformset_factory(Venta, VentaDetalle, fields='__all__')

class CotizacionForm(ModelForm):
  class Meta:
    model = Cotizacion
    fields = '__all__'

CotizacionDetalleFormSet = inlineformset_factory(Cotizacion, CotizacionDetalle, fields='__all__')
