from django import forms
from .models import BoxData
from django.forms import formset_factory

class BoxOrderForm(forms.Form):
    sku_name = forms.ChoiceField(
        choices=[('', '---------')] + [(box.sku_name, box.sku_name) for box in BoxData.objects.all()],
        widget=forms.Select(attrs={'class': 'sku-select'}),
        label='Select Box (SKU)'
    )
    quantity = forms.IntegerField(min_value=1, label='Quantity')

BoxOrderFormSet = forms.formset_factory(BoxOrderForm, extra=0, can_delete=True)