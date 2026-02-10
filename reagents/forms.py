# reagents/forms.py

from django import forms
from .models import Reagent
from django.forms.widgets import NumberInput

class ReagentForm(forms.ModelForm):
    # Using NumberInput widget for opening_quantity to get up/down arrows
    opening_quantity = forms.IntegerField(widget=NumberInput(attrs={'type': 'number', 'min': 0}))  # Minimum value can be 0

    class Meta:
        model = Reagent
        fields = ['item_received_date', 'expiration_date', 'lot_number', 'name', 'vendor', 
                  'received_qty', 'opening_quantity', 'quantity_in_stock', 'on_order', 'category']
