from django import forms
from django.forms.models import inlineformset_factory

from models import Entrada, EntradaDetalle, Salida, SalidaDetalle

class EntradaForm(forms.ModelForm):
  class Meta:
    model = Entrada
    fields = '__all__'

EntradaDetalleFormSet = inlineformset_factory(Entrada, EntradaDetalle, fields='__all__')

class SalidaForm(forms.ModelForm):
  class Meta:
    model = Salida
    fields = '__all__'

SalidaDetalleFormSet = inlineformset_factory(Salida, SalidaDetalle, fields='__all__')
