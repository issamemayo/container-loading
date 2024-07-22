from django import forms
from .models import BoxData,TruckData
from django.forms import formset_factory

class PalletForm(forms.Form):
    box = forms.ModelChoiceField(
        queryset=BoxData.objects.all(),
        required=True,
        label="Select Box",
        help_text="Select the box you want to use"
    )
    pallet_length = forms.IntegerField(
        required=True,
        initial=1200,
        label="Pallet Length (mm)",
        help_text="Enter the length of the pallet in mm"
    )
    pallet_breadth = forms.IntegerField(
        required=True,
        initial=1000,
        label="Pallet Breadth (mm)",
        help_text="Enter the breadth of the pallet in mm"
    )
    pallet_height = forms.IntegerField(
        required=True,
        initial=2200,
        label="Pallet Height (mm)",
        help_text="Enter the height of the pallet in mm"
    )

    from django import forms

class CargoForm(forms.Form):
    truck_type=forms.ModelChoiceField(
        queryset=TruckData.objects.all(),
        required=True,
        label="Select Truck Number",
        help_text="Select the Truck to load boxes into"
    )
    B1_count = forms.IntegerField(label='Count of B1 Boxes', min_value=0, initial=1000)
    B2_count = forms.IntegerField(label='Count of B2 Boxes', min_value=0, initial=908)
    B3_count = forms.IntegerField(label='Count of B3 Boxes', min_value=0, initial=350)
