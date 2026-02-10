from django.contrib import admin
from django.utils.html import format_html  # Make sure this is imported
from .models import Patient, LabOrder, TestResult  # Ensure your models are imported
from .forms import LabOrderForm  # Import the custom form for LabOrder

# Create a custom admin class for the Patient model
class PatientAdmin(admin.ModelAdmin):
    list_display = ('OP_NO', 'full_name', 'age_gender', 'nationality', 'client_name', 'date_added', 'barcode_image_display')  # Added barcode_image_display
    search_fields = ['OP_NO', 'first_name', 'last_name', 'client_name']
    list_filter = ('date_added', 'nationality', 'gender', 'age', 'client_name')

    # Method to display full name (combining first and last name)
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.admin_order_field = 'first_name'  # Make it sortable by first name

    # Method to display age and gender in one column
    def age_gender(self, obj):
        return f"{obj.age}/{obj.gender}"
    age_gender.admin_order_field = 'age'  # Make it sortable by age

    # Method to display client name
    def client_name(self, obj):
        return obj.client_name
    client_name.admin_order_field = 'client_name'
    client_name.short_description = 'Client Name'

    # Method to display the barcode image in the admin list view
    def barcode_image_display(self, obj):
        if obj.barcode_image:
            return format_html('<img src="{}" width="100" height="100"/>', obj.barcode_image.url)
        return "No Barcode"
    barcode_image_display.short_description = 'Barcode'
    
    # Method to generate the barcode link
    def print_barcode_link(self, obj):
        if obj.OP_NO:
            barcode_url = f"{obj.barcode_image_url}"
            return format_html('<a href="{}" target="_blank">Print Barcode</a>', barcode_url)
        return "No Barcode Available"
    print_barcode_link.short_description = "Barcode Link"

# Create a custom admin class for the LabOrder model
class LabOrderAdmin(admin.ModelAdmin):
    form = LabOrderForm  # Use the custom form with dynamic test_name based on test_type
    list_display = ('patient_op_no', 'patient_full_name', 'test_id', 'test_type', 'test_name', 'sample_type', 'container', 'sample_collected', 'sample_insufficient', 'date', 'remarks')

    # Add the new field "Sample Insufficient" to the list view
    list_filter = ('test_type', 'test_name', 'sample_type', 'sample_collected', 'container', 'date')
    search_fields = ['test_name', 'patient__OP_NO', 'sample_type', 'test_id']  # Added test_id to search fields

    fieldsets = (
        (None, {
            'fields': ('patient', 'test_id', 'test_type', 'test_name', 'sample_type', 'container', 'sample_collected', 'sample_insufficient', 'remarks', 'date')
        }),
    )

    class Media:
        js = ('lab_management/js/admin/test_name_update.js',)  # Ensure this path is correct

    # Method to display OP_NO of the patient in the list
    def patient_op_no(self, obj):
        return obj.patient.OP_NO
    patient_op_no.admin_order_field = 'patient__OP_NO'
    patient_op_no.short_description = 'OP NO'

    # Method to display full name of the patient
    def patient_full_name(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}"
    patient_full_name.admin_order_field = 'patient__first_name'
    patient_full_name.short_description = 'Patient Name'

    # Method to show the container field properly in the admin list
    def container(self, obj):
        return obj.container
    container.admin_order_field = 'container'
    container.short_description = 'Container'

# Register the Patient model with the custom admin class
admin.site.register(Patient, PatientAdmin)

# Register the LabOrder model with the custom admin class
admin.site.register(LabOrder, LabOrderAdmin)

# Register the TestResult model as it is
admin.site.register(TestResult)
