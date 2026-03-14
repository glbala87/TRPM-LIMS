# equipment/forms.py

from django import forms
from .models import InstrumentType, Instrument, MaintenanceRecord


class InstrumentTypeForm(forms.ModelForm):
    class Meta:
        model = InstrumentType
        fields = ['name', 'code', 'description', 'manufacturer',
                  'maintenance_interval_days', 'calibration_interval_days', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class InstrumentForm(forms.ModelForm):
    class Meta:
        model = Instrument
        fields = ['name', 'instrument_type', 'serial_number', 'asset_number',
                  'manufacturer', 'model', 'firmware_version', 'software_version',
                  'status', 'location', 'purchase_date', 'warranty_expiration',
                  'installation_date', 'last_maintenance', 'next_maintenance',
                  'last_calibration', 'next_calibration', 'contact_person',
                  'contact_phone', 'contact_email', 'notes', 'is_active']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'warranty_expiration': forms.DateInput(attrs={'type': 'date'}),
            'installation_date': forms.DateInput(attrs={'type': 'date'}),
            'last_maintenance': forms.DateInput(attrs={'type': 'date'}),
            'next_maintenance': forms.DateInput(attrs={'type': 'date'}),
            'last_calibration': forms.DateInput(attrs={'type': 'date'}),
            'next_calibration': forms.DateInput(attrs={'type': 'date'}),
        }


class MaintenanceRecordForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        fields = ['instrument', 'maintenance_type', 'status', 'scheduled_date',
                  'performed_at', 'completed_at', 'performed_by', 'service_provider',
                  'description', 'findings', 'actions_taken', 'parts_replaced',
                  'cost', 'next_due', 'certificate', 'certificate_number',
                  'passed', 'notes']
        widgets = {
            'scheduled_date': forms.DateInput(attrs={'type': 'date'}),
            'performed_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'completed_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'next_due': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'findings': forms.Textarea(attrs={'rows': 3}),
            'actions_taken': forms.Textarea(attrs={'rows': 3}),
            'parts_replaced': forms.Textarea(attrs={'rows': 2}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
