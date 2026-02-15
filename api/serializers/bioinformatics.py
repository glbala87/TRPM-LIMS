"""
Serializers for bioinformatics app models.
"""
from rest_framework import serializers
from bioinformatics.models import (
    Pipeline, PipelineParameter, BioinformaticsService,
    AnalysisJob, AnalysisResult, ServiceDelivery
)


class PipelineParameterSerializer(serializers.ModelSerializer):
    """Serializer for PipelineParameter model."""
    param_type_display = serializers.CharField(source='get_param_type_display', read_only=True)

    class Meta:
        model = PipelineParameter
        fields = [
            'id', 'pipeline', 'name', 'display_name', 'description',
            'param_type', 'param_type_display', 'default_value', 'choices',
            'is_required', 'order'
        ]


class PipelineSerializer(serializers.ModelSerializer):
    """Serializer for Pipeline model."""
    pipeline_type_display = serializers.CharField(source='get_pipeline_type_display', read_only=True)
    executor_display = serializers.CharField(source='get_executor_display', read_only=True)
    parameters = PipelineParameterSerializer(many=True, read_only=True)

    class Meta:
        model = Pipeline
        fields = [
            'id', 'code', 'name', 'version', 'description',
            'pipeline_type', 'pipeline_type_display', 'executor', 'executor_display',
            'repository_url', 'config_file',
            'default_cpu', 'default_memory_gb', 'default_time_hours',
            'is_active', 'parameters', 'created_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at']


class PipelineListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Pipeline list views."""
    pipeline_type_display = serializers.CharField(source='get_pipeline_type_display', read_only=True)
    executor_display = serializers.CharField(source='get_executor_display', read_only=True)

    class Meta:
        model = Pipeline
        fields = ['id', 'code', 'name', 'version', 'pipeline_type_display', 'executor_display', 'is_active']


class AnalysisResultSerializer(serializers.ModelSerializer):
    """Serializer for AnalysisResult model."""
    result_type_display = serializers.CharField(source='get_result_type_display', read_only=True)

    class Meta:
        model = AnalysisResult
        fields = [
            'id', 'job', 'result_type', 'result_type_display',
            'file_path', 'file_size_bytes', 'checksum_md5', 'description', 'created_at'
        ]


class AnalysisJobSerializer(serializers.ModelSerializer):
    """Serializer for AnalysisJob model."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    results = AnalysisResultSerializer(many=True, read_only=True)

    class Meta:
        model = AnalysisJob
        fields = [
            'id', 'job_id', 'service', 'sample', 'status', 'status_display',
            'cluster_job_id', 'work_directory', 'log_file',
            'cpu_hours', 'memory_peak_gb', 'runtime_seconds', 'exit_code', 'error_message',
            'submitted_at', 'started_at', 'completed_at', 'created_at', 'results'
        ]
        read_only_fields = ['id', 'job_id', 'created_at']


class AnalysisJobListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for AnalysisJob list views."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = AnalysisJob
        fields = ['id', 'job_id', 'service', 'status_display', 'runtime_seconds', 'created_at']


class ServiceDeliverySerializer(serializers.ModelSerializer):
    """Serializer for ServiceDelivery model."""
    delivery_method_display = serializers.CharField(source='get_delivery_method_display', read_only=True)

    class Meta:
        model = ServiceDelivery
        fields = [
            'id', 'service', 'delivery_method', 'delivery_method_display',
            'delivery_path', 'delivery_url', 'files_included', 'report_file',
            'delivered_at', 'delivered_by', 'acknowledged_at', 'notes'
        ]


class BioinformaticsServiceSerializer(serializers.ModelSerializer):
    """Serializer for BioinformaticsService model."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    pipeline_name = serializers.CharField(source='pipeline.name', read_only=True)
    jobs = AnalysisJobListSerializer(many=True, read_only=True)
    deliveries = ServiceDeliverySerializer(many=True, read_only=True)

    class Meta:
        model = BioinformaticsService
        fields = [
            'id', 'service_id', 'pipeline', 'pipeline_name', 'title', 'description',
            'priority', 'priority_display', 'status', 'status_display',
            'samples', 'instrument_runs', 'parameters', 'output_directory', 'notes',
            'requested_at', 'approved_at', 'started_at', 'completed_at', 'delivered_at',
            'requested_by', 'approved_by', 'assigned_to',
            'jobs', 'deliveries'
        ]
        read_only_fields = ['id', 'service_id', 'requested_at', 'approved_at', 'started_at', 'completed_at', 'delivered_at']


class BioinformaticsServiceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for BioinformaticsService list views."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    pipeline_name = serializers.CharField(source='pipeline.name', read_only=True)

    class Meta:
        model = BioinformaticsService
        fields = ['id', 'service_id', 'title', 'pipeline_name', 'status_display', 'requested_at']
