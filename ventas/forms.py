from django import forms
from django.forms.models import inlineformset_factory

from models import Venta, VentaDetalle, Cotizacion, CotizacionDetalle

class VentaForm(forms.ModelForm):
  class Meta:
    model = Venta

DetalleFormSet = inlineformset_factory(Venta, VentaDetalle)

class CotizacionForm(forms.ModelForm):
  class Meta:
    model = Cotizacion

CotizacionDetalleFormSet = inlineformset_factory(Cotizacion, CotizacionDetalle)