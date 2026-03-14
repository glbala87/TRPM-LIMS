# storage/forms.py

from django import forms
from .models import StorageUnit, StorageRack, StorageLog


class StorageUnitForm(forms.ModelForm):
    class Meta:
        model = StorageUnit
        fields = ['name', 'code', 'unit_type', 'location', 'temperature_min',
                  'temperature_max', 'temperature_target', 'status', 'manufacturer',
                  'model', 'serial_number', 'capacity_description',
                  'has_temperature_monitoring', 'has_alarm', 'notes', 'is_active']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class StorageRackForm(forms.ModelForm):
    class Meta:
        model = StorageRack
        fields = ['unit', 'rack_id', 'name', 'shelf_number', 'rows', 'columns',
                  'rack_type', 'notes', 'is_active']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }


class StorageLogForm(forms.ModelForm):
    class Meta:
        model = StorageLog
        fields = ['position', 'sample_id', 'action', 'from_position',
                  'to_position', 'reason', 'notes']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 2}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
