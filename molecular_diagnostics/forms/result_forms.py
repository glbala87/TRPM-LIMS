# molecular_diagnostics/forms/result_forms.py

from django import forms
from django.forms import inlineformset_factory
from ..models import MolecularResult, PCRResult, VariantCall, GeneTarget


class MolecularResultForm(forms.ModelForm):
    """Form for entering molecular test results"""

    class Meta:
        model = MolecularResult
        fields = [
            'sample', 'test_panel', 'status', 'interpretation',
            'result_summary', 'clinical_significance',
            'recommendations', 'limitations', 'notes'
        ]
        widgets = {
            'result_summary': forms.Textarea(attrs={'rows': 4}),
            'clinical_significance': forms.Textarea(attrs={'rows': 4}),
            'recommendations': forms.Textarea(attrs={'rows': 3}),
            'limitations': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }


class PCRResultForm(forms.ModelForm):
    """Form for entering individual PCR target results"""

    class Meta:
        model = PCRResult
        fields = [
            'target_gene', 'ct_value', 'is_detected',
            'quantity', 'quantity_unit', 'replicate_number', 'well_position'
        ]
        widgets = {
            'ct_value': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '50'}),
            'quantity': forms.NumberInput(attrs={'step': '0.0001'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        ct_value = cleaned_data.get('ct_value')
        is_detected = cleaned_data.get('is_detected')

        # Auto-determine detection if Ct value is provided
        if ct_value is not None and not is_detected:
            if ct_value <= 40:
                cleaned_data['is_detected'] = 'DETECTED'
            else:
                cleaned_data['is_detected'] = 'NOT_DETECTED'

        return cleaned_data


PCRResultFormSet = inlineformset_factory(
    MolecularResult,
    PCRResult,
    form=PCRResultForm,
    extra=1,
    can_delete=True,
)


class VariantCallForm(forms.ModelForm):
    """Form for entering variant calls"""

    class Meta:
        model = VariantCall
        fields = [
            'gene', 'chromosome', 'position', 'ref_allele', 'alt_allele',
            'hgvs_c', 'hgvs_p', 'variant_type', 'consequence',
            'classification', 'zygosity',
            'allele_frequency', 'read_depth',
            'dbsnp_id', 'clinvar_id', 'cosmic_id',
            'population_frequency',
            'is_reportable', 'interpretation', 'notes'
        ]
        widgets = {
            'ref_allele': forms.TextInput(attrs={'style': 'font-family: monospace;'}),
            'alt_allele': forms.TextInput(attrs={'style': 'font-family: monospace;'}),
            'hgvs_c': forms.TextInput(attrs={'placeholder': 'c.1234A>G'}),
            'hgvs_p': forms.TextInput(attrs={'placeholder': 'p.Arg123Gly'}),
            'allele_frequency': forms.NumberInput(attrs={'step': '0.0001', 'min': '0', 'max': '1'}),
            'population_frequency': forms.NumberInput(attrs={'step': '0.000001', 'min': '0', 'max': '1'}),
            'interpretation': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }


VariantCallFormSet = inlineformset_factory(
    MolecularResult,
    VariantCall,
    form=VariantCallForm,
    extra=1,
    can_delete=True,
)


class SampleTransitionForm(forms.Form):
    """Form for transitioning a sample to a new workflow status"""

    new_status = forms.ChoiceField(choices=[])
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text="Optional notes about this transition"
    )
    qc_passed = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=[
            ('', '---------'),
            ('true', 'Passed'),
            ('false', 'Failed'),
        ])
    )
    qc_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2}),
        help_text="QC-related notes"
    )

    def __init__(self, *args, available_transitions=None, **kwargs):
        super().__init__(*args, **kwargs)
        if available_transitions:
            self.fields['new_status'].choices = available_transitions


class PlateLayoutForm(forms.Form):
    """Form for assigning samples to plate wells"""

    position = forms.CharField(max_length=4)
    sample = forms.ModelChoiceField(
        queryset=None,
        required=False
    )
    control_type = forms.ChoiceField(
        choices=[
            ('', 'Sample'),
            ('POSITIVE', 'Positive Control'),
            ('NEGATIVE', 'Negative Control'),
            ('NTC', 'No Template Control'),
            ('EMPTY', 'Empty'),
        ],
        required=False
    )

    def __init__(self, *args, sample_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        if sample_queryset is not None:
            self.fields['sample'].queryset = sample_queryset
