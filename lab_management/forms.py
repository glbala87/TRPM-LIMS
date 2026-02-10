from django import forms
from .models import Patient, LabOrder, TestResult, TEST_CHOICES  # Ensure the models are imported


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = '__all__'


class LabOrderForm(forms.ModelForm):
    class Meta:
        model = LabOrder
        fields = ['patient', 'test_id', 'test_type', 'test_name', 'sample_type', 'container', 'sample_collected', 'sample_insufficient', 'remarks', 'date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamically populate the test_name choices based on the selected test_type
        if 'test_type' in self.data:
            test_type = self.data.get('test_type')
            if test_type in TEST_CHOICES:
                self.fields['test_name'].choices = [(test[0], test[0]) for test in TEST_CHOICES[test_type]]

        elif self.instance and self.instance.test_type:
            test_type = self.instance.test_type
            if test_type in TEST_CHOICES:
                self.fields['test_name'].choices = [(test[0], test[0]) for test in TEST_CHOICES[test_type]]

    def save(self, commit=True):
        instance = super().save(commit=False)
        for category, tests in TEST_CHOICES.items():
            if instance.test_name:
                for test in tests:
                    if test[0] == instance.test_name:
                        instance.sample_type = test[1]
                        instance.container = test[2]
                        break
        if commit:
            instance.save()
        return instance
    
class TestResultForm(forms.ModelForm):
    class Meta:
        model = TestResult
        fields = '__all__'


class PatientSearchForm(forms.Form):
    op_no = forms.CharField(label='Search by OP NO', max_length=20, required=False)
