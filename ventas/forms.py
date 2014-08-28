from django import forms
from django.forms.models import inlineformset_factory

from models import Venta, VentaDetalle

class VentaForm(forms.ModelForm):
  class Meta:
    model = Venta

DetalleFormSet = inlineformset_factory(Venta, VentaDetalle)