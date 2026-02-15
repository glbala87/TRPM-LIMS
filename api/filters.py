"""
Filter classes for the TRPM-LIMS REST API.
"""
from django.db import models
from django_filters import rest_framework as filters

from lab_management.models import Patient, LabOrder, TestResult
from molecular_diagnostics.models import (
    MolecularSample, MolecularSampleType, MolecularTestPanel, GeneTarget,
    MolecularResult, PCRResult, SequencingResult, VariantCall,
    PCRPlate, InstrumentRun, NGSLibrary, NGSPool,
    QCMetricDefinition, ControlSample, QCRecord
)
from equipment.models import Instrument, InstrumentType, MaintenanceRecord
from storage.models import StorageUnit, StorageRack, StoragePosition, StorageLog
from reagents.models import Reagent, MolecularReagent


# Lab Management Filters

class PatientFilter(filters.FilterSet):
    """Filter for Patient records."""
    first_name = filters.CharFilter(lookup_expr='icontains')
    last_name = filters.CharFilter(lookup_expr='icontains')
    op_no = filters.CharFilter(field_name='OP_NO', lookup_expr='iexact')
    gender = filters.CharFilter(lookup_expr='iexact')
    added_after = filters.DateFilter(field_name='date_added', lookup_expr='gte')
    added_before = filters.DateFilter(field_name='date_added', lookup_expr='lte')
    client_name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'op_no', 'gender', 'client_name']


class LabOrderFilter(filters.FilterSet):
    """Filter for Lab Order records."""
    patient = filters.NumberFilter(field_name='patient__id')
    patient_name = filters.CharFilter(method='filter_patient_name')
    test_type = filters.CharFilter(lookup_expr='iexact')
    date_after = filters.DateFilter(field_name='date', lookup_expr='gte')
    date_before = filters.DateFilter(field_name='date', lookup_expr='lte')
    collected = filters.BooleanFilter(field_name='sample_collected')

    class Meta:
        model = LabOrder
        fields = ['patient', 'test_type', 'sample_collected']

    def filter_patient_name(self, queryset, name, value):
        return queryset.filter(
            models.Q(patient__first_name__icontains=value) |
            models.Q(patient__last_name__icontains=value)
        )


class TestResultFilter(filters.FilterSet):
    """Filter for Test Result records."""
    lab_order = filters.NumberFilter(field_name='lab_order__id')
    result_updated = filters.BooleanFilter()

    class Meta:
        model = TestResult
        fields = ['lab_order', 'result_updated']


# Molecular Diagnostics Filters

class MolecularSampleFilter(filters.FilterSet):
    """Filter for Molecular Sample records."""
    sample_id = filters.CharFilter(lookup_expr='icontains')
    workflow_status = filters.CharFilter(lookup_expr='iexact')
    priority = filters.CharFilter(lookup_expr='iexact')
    sample_type = filters.NumberFilter(field_name='sample_type__id')
    received_after = filters.DateTimeFilter(field_name='received_datetime', lookup_expr='gte')
    received_before = filters.DateTimeFilter(field_name='received_datetime', lookup_expr='lte')
    lab_order = filters.NumberFilter(field_name='lab_order__id')
    is_active = filters.BooleanFilter()

    class Meta:
        model = MolecularSample
        fields = ['sample_id', 'workflow_status', 'priority', 'sample_type', 'is_active']


class MolecularTestPanelFilter(filters.FilterSet):
    """Filter for Molecular Test Panel records."""
    name = filters.CharFilter(lookup_expr='icontains')
    code = filters.CharFilter(lookup_expr='iexact')
    test_type = filters.CharFilter(lookup_expr='iexact')
    is_active = filters.BooleanFilter()
    gene_target = filters.NumberFilter(field_name='gene_targets__id')

    class Meta:
        model = MolecularTestPanel
        fields = ['name', 'code', 'test_type', 'is_active']


class GeneTargetFilter(filters.FilterSet):
    """Filter for Gene Target records."""
    symbol = filters.CharFilter(lookup_expr='icontains')
    chromosome = filters.CharFilter(lookup_expr='iexact')
    is_active = filters.BooleanFilter()

    class Meta:
        model = GeneTarget
        fields = ['symbol', 'chromosome', 'is_active']


class MolecularResultFilter(filters.FilterSet):
    """Filter for Molecular Result records."""
    sample = filters.NumberFilter(field_name='sample__id')
    test_panel = filters.NumberFilter(field_name='test_panel__id')
    status = filters.CharFilter(lookup_expr='iexact')
    interpretation = filters.CharFilter(lookup_expr='iexact')
    performed_after = filters.DateTimeFilter(field_name='performed_at', lookup_expr='gte')

    class Meta:
        model = MolecularResult
        fields = ['sample', 'test_panel', 'status', 'interpretation']


class VariantCallFilter(filters.FilterSet):
    """Filter for Variant Call records."""
    result = filters.NumberFilter(field_name='result__id')
    gene_target = filters.NumberFilter(field_name='gene_target__id')
    chromosome = filters.CharFilter(lookup_expr='iexact')
    classification = filters.CharFilter(lookup_expr='iexact')
    zygosity = filters.CharFilter(lookup_expr='iexact')
    is_reportable = filters.BooleanFilter()
    dbsnp_id = filters.CharFilter(lookup_expr='iexact')
    clinvar_id = filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = VariantCall
        fields = ['result', 'gene_target', 'chromosome', 'classification', 'zygosity', 'is_reportable']


class PCRPlateFilter(filters.FilterSet):
    """Filter for PCR Plate records."""
    barcode = filters.CharFilter(lookup_expr='icontains')
    plate_type = filters.CharFilter(lookup_expr='iexact')
    instrument_run = filters.NumberFilter(field_name='instrument_run__id')
    created_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')

    class Meta:
        model = PCRPlate
        fields = ['barcode', 'plate_type', 'instrument_run']


class InstrumentRunFilter(filters.FilterSet):
    """Filter for Instrument Run records."""
    run_id = filters.CharFilter(lookup_expr='icontains')
    instrument = filters.NumberFilter(field_name='instrument__id')
    status = filters.CharFilter(lookup_expr='iexact')
    started_after = filters.DateTimeFilter(field_name='start_time', lookup_expr='gte')
    completed_before = filters.DateTimeFilter(field_name='end_time', lookup_expr='lte')

    class Meta:
        model = InstrumentRun
        fields = ['run_id', 'instrument', 'status']


class QCRecordFilter(filters.FilterSet):
    """Filter for QC Record records."""
    instrument_run = filters.NumberFilter(field_name='instrument_run__id')
    plate = filters.NumberFilter(field_name='plate__id')
    metric = filters.NumberFilter(field_name='metric__id')
    status = filters.CharFilter(lookup_expr='iexact')
    recorded_after = filters.DateTimeFilter(field_name='recorded_at', lookup_expr='gte')

    class Meta:
        model = QCRecord
        fields = ['instrument_run', 'plate', 'metric', 'status']


# Equipment Filters

class InstrumentFilter(filters.FilterSet):
    """Filter for Instrument records."""
    name = filters.CharFilter(lookup_expr='icontains')
    serial_number = filters.CharFilter(lookup_expr='iexact')
    instrument_type = filters.NumberFilter(field_name='instrument_type__id')
    status = filters.CharFilter(lookup_expr='iexact')
    location = filters.CharFilter(lookup_expr='icontains')
    maintenance_due = filters.BooleanFilter(method='filter_maintenance_due')

    class Meta:
        model = Instrument
        fields = ['name', 'serial_number', 'instrument_type', 'status', 'location']

    def filter_maintenance_due(self, queryset, name, value):
        from django.utils import timezone
        if value:
            return queryset.filter(next_maintenance_date__lte=timezone.now().date())
        return queryset.filter(next_maintenance_date__gt=timezone.now().date())


class MaintenanceRecordFilter(filters.FilterSet):
    """Filter for Maintenance Record records."""
    instrument = filters.NumberFilter(field_name='instrument__id')
    maintenance_type = filters.CharFilter(lookup_expr='iexact')
    status = filters.CharFilter(lookup_expr='iexact')
    scheduled_after = filters.DateFilter(field_name='scheduled_date', lookup_expr='gte')
    completed_after = filters.DateFilter(field_name='completed_date', lookup_expr='gte')

    class Meta:
        model = MaintenanceRecord
        fields = ['instrument', 'maintenance_type', 'status']


# Storage Filters

class StorageUnitFilter(filters.FilterSet):
    """Filter for Storage Unit records."""
    name = filters.CharFilter(lookup_expr='icontains')
    unit_type = filters.CharFilter(lookup_expr='iexact')
    status = filters.CharFilter(lookup_expr='iexact')
    location = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = StorageUnit
        fields = ['name', 'unit_type', 'status', 'location']


class StoragePositionFilter(filters.FilterSet):
    """Filter for Storage Position records."""
    rack = filters.NumberFilter(field_name='rack__id')
    is_occupied = filters.BooleanFilter()
    is_reserved = filters.BooleanFilter()
    stored_after = filters.DateFilter(field_name='stored_at', lookup_expr='gte')

    class Meta:
        model = StoragePosition
        fields = ['rack', 'is_occupied', 'is_reserved']


class StorageLogFilter(filters.FilterSet):
    """Filter for Storage Log records."""
    action = filters.CharFilter(lookup_expr='iexact')
    user = filters.NumberFilter(field_name='user__id')
    timestamp_after = filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    timestamp_before = filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')

    class Meta:
        model = StorageLog
        fields = ['action', 'user']


# Reagent Filters

class ReagentFilter(filters.FilterSet):
    """Filter for Reagent records."""
    name = filters.CharFilter(lookup_expr='icontains')
    category = filters.CharFilter(lookup_expr='iexact')
    lot_number = filters.CharFilter(lookup_expr='iexact')
    is_expired = filters.BooleanFilter(method='filter_expired')
    low_stock = filters.BooleanFilter(method='filter_low_stock')

    class Meta:
        model = Reagent
        fields = ['name', 'category', 'lot_number']

    def filter_expired(self, queryset, name, value):
        from django.utils import timezone
        if value:
            return queryset.filter(expiration_date__lt=timezone.now().date())
        return queryset.filter(expiration_date__gte=timezone.now().date())

    def filter_low_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock_quantity__lt=10)
        return queryset


class MolecularReagentFilter(filters.FilterSet):
    """Filter for Molecular Reagent records."""
    name = filters.CharFilter(lookup_expr='icontains')
    category = filters.CharFilter(lookup_expr='iexact')
    lot_number = filters.CharFilter(lookup_expr='iexact')
    catalog_number = filters.CharFilter(lookup_expr='iexact')
    is_expired = filters.BooleanFilter(method='filter_expired')
    is_validated = filters.BooleanFilter()
    test_panel = filters.NumberFilter(field_name='test_panels__id')
    gene_target = filters.NumberFilter(field_name='gene_targets__id')

    class Meta:
        model = MolecularReagent
        fields = ['name', 'category', 'lot_number', 'catalog_number', 'is_validated']

    def filter_expired(self, queryset, name, value):
        from django.utils import timezone
        if value:
            return queryset.filter(expiration_date__lt=timezone.now().date())
        return queryset.filter(expiration_date__gte=timezone.now().date())
