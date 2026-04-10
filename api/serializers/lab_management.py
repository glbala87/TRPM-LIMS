"""
Serializers for lab_management app models.
Field lists are aligned with the actual model definitions in lab_management/models.py.
"""
from rest_framework import serializers
from lab_management.models import Patient, LabOrder, TestResult


class PatientSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    barcode_url = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            'id', 'OP_NO', 'first_name', 'middle_name', 'last_name', 'full_name',
            'tribe', 'age', 'gender', 'marital_status', 'nationality',
            'phone_no', 'passport_no', 'resident_card', 'client_name',
            'is_special', 'is_company', 'date_added', 'barcode_url',
        ]
        read_only_fields = ['id', 'OP_NO', 'date_added', 'barcode_url']

    def get_full_name(self, obj):
        return obj.get_full_name() if hasattr(obj, 'get_full_name') else f"{obj.first_name} {obj.last_name}"

    def get_barcode_url(self, obj):
        if obj.barcode_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.barcode_image.url)
            return obj.barcode_image.url
        return None


class PatientListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ['id', 'OP_NO', 'full_name', 'gender', 'age', 'client_name', 'date_added']

    def get_full_name(self, obj):
        return obj.get_full_name() if hasattr(obj, 'get_full_name') else f"{obj.first_name} {obj.last_name}"


class PatientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            'first_name', 'middle_name', 'last_name', 'tribe', 'age', 'gender',
            'marital_status', 'nationality', 'phone_no', 'passport_no',
            'resident_card', 'client_name', 'is_special', 'is_company',
        ]


class TestResultSerializer(serializers.ModelSerializer):
    lab_order_id = serializers.IntegerField(source='lab_order.id', read_only=True)

    class Meta:
        model = TestResult
        fields = ['id', 'lab_order_id', 'result_data', 'result_updated']
        read_only_fields = ['id', 'result_updated']


class LabOrderSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    patient_op_no = serializers.CharField(source='patient.OP_NO', read_only=True)
    test_type_display = serializers.CharField(source='get_test_type_display', read_only=True)
    result = TestResultSerializer(source='testresult', read_only=True)

    class Meta:
        model = LabOrder
        fields = [
            'id', 'patient', 'patient_name', 'patient_op_no',
            'test_id', 'test_type', 'test_type_display', 'test_name',
            'sample_type', 'container',
            'sample_collected', 'sample_insufficient', 'remarks', 'date',
            'result',
        ]
        read_only_fields = ['id']

    def get_patient_name(self, obj):
        return obj.patient.get_full_name() if hasattr(obj.patient, 'get_full_name') else f"{obj.patient.first_name} {obj.patient.last_name}"


class LabOrderListSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    patient_op_no = serializers.CharField(source='patient.OP_NO', read_only=True)
    test_type_display = serializers.CharField(source='get_test_type_display', read_only=True)

    class Meta:
        model = LabOrder
        fields = [
            'id', 'patient_name', 'patient_op_no', 'test_type_display',
            'test_name', 'sample_collected', 'date',
        ]

    def get_patient_name(self, obj):
        return obj.patient.get_full_name() if hasattr(obj.patient, 'get_full_name') else f"{obj.patient.first_name} {obj.patient.last_name}"


class LabOrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabOrder
        fields = [
            'patient', 'test_type', 'test_name', 'sample_type', 'container', 'remarks',
        ]

    def validate(self, data):
        # Auto-populate sample_type and container based on test_name when a mapping exists.
        test_name = data.get('test_name')
        mapping = getattr(LabOrder, 'TEST_SAMPLE_MAPPING', {}).get(test_name, {}) if test_name else {}
        if mapping:
            if not data.get('sample_type'):
                data['sample_type'] = mapping.get('sample_type', '')
            if not data.get('container'):
                data['container'] = mapping.get('container', '')
        return data
