from django import forms
from django.forms.models import inlineformset_factory

from models import Entrada, EntradaDetalle, Salida, SalidaDetalle

class EntradaForm(forms.ModelForm):
  class Meta:
    model = Entrada

EntradaDetalleFormSet = inlineformset_factory(Entrada, EntradaDetalle)

class SalidaForm(forms.ModelForm):
  class Meta:
    model = Salida

SalidaDetalleFormSet = inlineformset_factory(Salida, SalidaDetalle)