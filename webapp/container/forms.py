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
    tolerance_limit=forms.IntegerField(label="Enter tolerance limit (in mm)", min_value=0,initial=0)
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
    

   

class CargoForm(forms.Form):
    truck_type=forms.ModelChoiceField(
        queryset=TruckData.objects.all(),
        required=True,
        label="Select Truck Number",
        help_text="Select the Truck to load boxes into"
    )
    max_weight=forms.IntegerField(label="Enter max weight of truck permissible", initial=12500)
    tolerance_limit=forms.IntegerField(label="Enter tolerance limit (in mm)", min_value=0,initial=0)


class BoxTypeForm(forms.Form):
    
    box_type=forms.ModelChoiceField(
        queryset=BoxData.objects.all(),
        required=True,
        label="Select Box",
        
    )
    
    number=forms.IntegerField(label="Enter number of boxes", min_value=0, initial=0)
    

BoxTypeFormSet=formset_factory(BoxTypeForm, extra=1)