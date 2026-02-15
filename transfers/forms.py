# transfers/forms.py

from django import forms
from django.forms import inlineformset_factory
from .models import Transfer, TransferItem


class TransferForm(forms.ModelForm):
    """Form for creating and editing transfers."""

    class Meta:
        model = Transfer
        fields = [
            'source_location',
            'destination_location',
            'courier',
            'tracking_number',
            'shipment_conditions',
            'expected_arrival_date',
            'notes',
            'special_instructions',
        ]
        widgets = {
            'source_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter source facility/location'
            }),
            'destination_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter destination facility/location'
            }),
            'courier': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., FedEx, DHL, Internal Courier'
            }),
            'tracking_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Shipping tracking number'
            }),
            'shipment_conditions': forms.Select(attrs={
                'class': 'form-control'
            }),
            'expected_arrival_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes about the transfer'
            }),
            'special_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Special handling instructions'
            }),
        }


class TransferItemForm(forms.ModelForm):
    """Form for adding/editing transfer items."""

    class Meta:
        model = TransferItem
        fields = [
            'sample_id',
            'quantity',
            'container_type',
            'storage_position',
            'condition_on_departure',
            'notes',
        ]
        widgets = {
            'sample_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sample ID'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'value': 1
            }),
            'container_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Cryovial, Tube'
            }),
            'storage_position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Position in shipping container'
            }),
            'condition_on_departure': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sample condition'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Notes about this item'
            }),
        }


# Inline formset for adding multiple items to a transfer
TransferItemFormSet = inlineformset_factory(
    Transfer,
    TransferItem,
    form=TransferItemForm,
    extra=3,
    can_delete=True,
    min_num=1,
    validate_min=True
)


class TransferReceiveForm(forms.Form):
    """Form for receiving a transfer."""

    received_by_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Receiver name (if different from logged-in user)'
        })
    )

    overall_condition = forms.ChoiceField(
        choices=[
            ('GOOD', 'Good - All samples in expected condition'),
            ('ACCEPTABLE', 'Acceptable - Minor issues noted'),
            ('DAMAGED', 'Damaged - Some samples affected'),
            ('CRITICAL', 'Critical - Major damage or loss'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Notes about the received shipment'
        })
    )


class TransferItemReceiveForm(forms.ModelForm):
    """Form for receiving individual transfer items."""

    class Meta:
        model = TransferItem
        fields = [
            'condition_on_arrival',
            'has_discrepancy',
            'discrepancy_notes',
        ]
        widgets = {
            'condition_on_arrival': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Condition on arrival'
            }),
            'has_discrepancy': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'discrepancy_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Describe any discrepancies'
            }),
        }


class TransferSearchForm(forms.Form):
    """Form for searching transfers."""

    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by transfer number, location, or tracking number'
        })
    )

    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Statuses')] + Transfer.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    courier = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Courier name'
        })
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )


class QuickTransferForm(forms.Form):
    """Simplified form for quick transfer creation."""

    source_location = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Source location'
        })
    )

    destination_location = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Destination location'
        })
    )

    sample_ids = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Enter sample IDs, one per line'
        }),
        help_text='Enter one sample ID per line'
    )

    shipment_conditions = forms.ChoiceField(
        choices=Transfer.SHIPMENT_CONDITION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    courier = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Courier name (optional)'
        })
    )

    def clean_sample_ids(self):
        """Parse sample IDs from textarea input."""
        data = self.cleaned_data['sample_ids']
        sample_ids = [
            sid.strip()
            for sid in data.strip().split('\n')
            if sid.strip()
        ]
        if not sample_ids:
            raise forms.ValidationError('At least one sample ID is required.')
        return sample_ids
