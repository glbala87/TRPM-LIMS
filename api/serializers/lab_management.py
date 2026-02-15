"""
Serializers for lab_management app models.
"""
from rest_framework import serializers
from lab_management.models import Patient, LabOrder, TestResult


class PatientSerializer(serializers.ModelSerializer):
    """Serializer for Patient model."""
    full_name = serializers.SerializerMethodField()
    barcode_url = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            'id', 'OP_NO', 'first_name', 'middle_name', 'last_name', 'full_name',
            'tribe', 'age', 'gender', 'marital_status', 'nationality',
            'passport_no', 'resident_card', 'client_name', 'is_special', 'is_company',
            'registered_date', 'barcode_url'
        ]
        read_only_fields = ['id', 'OP_NO', 'registered_date', 'barcode_url']

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_barcode_url(self, obj):
        if obj.barcode_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.barcode_image.url)
            return obj.barcode_image.url
        return None


class PatientListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Patient list views."""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ['id', 'OP_NO', 'full_name', 'gender', 'age', 'client_name', 'registered_date']

    def get_full_name(self, obj):
        return obj.get_full_name()


class PatientCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Patient records."""

    class Meta:
        model = Patient
        fields = [
            'first_name', 'middle_name', 'last_name', 'tribe', 'age', 'gender',
            'marital_status', 'nationality', 'passport_no', 'resident_card',
            'client_name', 'is_special', 'is_company'
        ]


class TestResultSerializer(serializers.ModelSerializer):
    """Serializer for TestResult model."""
    lab_order_id = serializers.IntegerField(source='lab_order.id', read_only=True)

    class Meta:
        model = TestResult
        fields = ['id', 'lab_order_id', 'result', 'result_updated', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class LabOrderSerializer(serializers.ModelSerializer):
    """Serializer for LabOrder model."""
    patient_name = serializers.SerializerMethodField()
    patient_op_no = serializers.CharField(source='patient.OP_NO', read_only=True)
    test_category_display = serializers.CharField(source='get_test_category_display', read_only=True)
    results = TestResultSerializer(many=True, read_only=True)

    class Meta:
        model = LabOrder
        fields = [
            'id', 'patient', 'patient_name', 'patient_op_no', 'test_category',
            'test_category_display', 'test_name', 'sample_type', 'container',
            'sample_collected', 'sample_insufficient', 'status', 'notes',
            'created_at', 'updated_at', 'results'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_patient_name(self, obj):
        return obj.patient.get_full_name()


class LabOrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for LabOrder list views."""
    patient_name = serializers.SerializerMethodField()
    patient_op_no = serializers.CharField(source='patient.OP_NO', read_only=True)
    test_category_display = serializers.CharField(source='get_test_category_display', read_only=True)

    class Meta:
        model = LabOrder
        fields = [
            'id', 'patient_name', 'patient_op_no', 'test_category_display',
            'test_name', 'sample_collected', 'status', 'created_at'
        ]

    def get_patient_name(self, obj):
        return obj.patient.get_full_name()


class LabOrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating LabOrder records."""

    class Meta:
        model = LabOrder
        fields = [
            'patient', 'test_category', 'test_name', 'sample_type', 'container',
            'notes'
        ]

    def validate(self, data):
        # Auto-populate sample_type and container based on test_name
        test_name = data.get('test_name')
        if test_name:
            mapping = LabOrder.TEST_SAMPLE_MAPPING.get(test_name, {})
            if 'sample_type' not in data or not data['sample_type']:
                data['sample_type'] = mapping.get('sample_type', '')
            if 'container' not in data or not data['container']:
                data['container'] = mapping.get('container', '')
        return data
