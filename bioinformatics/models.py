# bioinformatics/models.py
"""
Bioinformatics pipeline management models.
Inspired by iskylims drylab module.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class Pipeline(models.Model):
    """Definition of an analysis pipeline."""

    PIPELINE_TYPE_CHOICES = [
        ('VARIANT_CALLING', 'Variant Calling'), ('RNA_SEQ', 'RNA-Seq'),
        ('CHIP_SEQ', 'ChIP-Seq'), ('METAGENOMICS', 'Metagenomics'),
        ('SINGLE_CELL', 'Single-Cell'), ('WGS', 'Whole Genome'),
        ('WES', 'Whole Exome'), ('AMPLICON', 'Amplicon'), ('CUSTOM', 'Custom'),
    ]

    EXECUTOR_CHOICES = [
        ('NEXTFLOW', 'Nextflow'), ('SNAKEMAKE', 'Snakemake'),
        ('WDL', 'WDL/Cromwell'), ('CWL', 'CWL'),
        ('BASH', 'Bash'), ('PYTHON', 'Python'),
    ]

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)
    version = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    pipeline_type = models.CharField(max_length=50, choices=PIPELINE_TYPE_CHOICES, default='VARIANT_CALLING')
    executor = models.CharField(max_length=20, choices=EXECUTOR_CHOICES, default='NEXTFLOW')
    repository_url = models.URLField(blank=True)
    config_file = models.TextField(blank=True)
    default_cpu = models.PositiveIntegerField(default=4)
    default_memory_gb = models.PositiveIntegerField(default=16)
    default_time_hours = models.PositiveIntegerField(default=24)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} v{self.version}"


class PipelineParameter(models.Model):
    """Parameters for a pipeline."""

    PARAM_TYPE_CHOICES = [
        ('STRING', 'String'), ('INTEGER', 'Integer'), ('FLOAT', 'Float'),
        ('BOOLEAN', 'Boolean'), ('FILE', 'File'), ('DIRECTORY', 'Directory'),
        ('SELECT', 'Selection'),
    ]

    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='parameters')
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    param_type = models.CharField(max_length=20, choices=PARAM_TYPE_CHOICES, default='STRING')
    default_value = models.TextField(blank=True)
    choices = models.JSONField(default=list, blank=True)
    is_required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['pipeline', 'order']
        unique_together = [['pipeline', 'name']]

    def __str__(self):
        return f"{self.pipeline.name}: {self.display_name}"


class BioinformaticsService(models.Model):
    """Bioinformatics service request."""

    STATUS_CHOICES = [
        ('REQUESTED', 'Requested'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected'),
        ('QUEUED', 'Queued'), ('RUNNING', 'Running'), ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'), ('DELIVERED', 'Delivered'), ('ARCHIVED', 'Archived'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Low'), ('NORMAL', 'Normal'), ('HIGH', 'High'), ('URGENT', 'Urgent'),
    ]

    service_id = models.CharField(max_length=50, unique=True, editable=False)
    pipeline = models.ForeignKey(Pipeline, on_delete=models.PROTECT, related_name='services')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='NORMAL')
    samples = models.ManyToManyField('molecular_diagnostics.MolecularSample', related_name='bioinformatics_services')
    instrument_runs = models.ManyToManyField('molecular_diagnostics.InstrumentRun', blank=True)
    parameters = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='REQUESTED')

    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='bio_requests')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='bio_approvals')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='bio_assignments')

    output_directory = models.CharField(max_length=500, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-requested_at']

    def save(self, *args, **kwargs):
        if not self.service_id:
            self.service_id = f"BIO-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_id}: {self.title}"


class AnalysisJob(models.Model):
    """Individual analysis job within a service."""

    STATUS_CHOICES = [
        ('PENDING', 'Pending'), ('SUBMITTED', 'Submitted'), ('RUNNING', 'Running'),
        ('COMPLETED', 'Completed'), ('FAILED', 'Failed'), ('CANCELLED', 'Cancelled'),
    ]

    job_id = models.CharField(max_length=100, unique=True)
    service = models.ForeignKey(BioinformaticsService, on_delete=models.CASCADE, related_name='jobs')
    sample = models.ForeignKey('molecular_diagnostics.MolecularSample', on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    cluster_job_id = models.CharField(max_length=100, blank=True)
    work_directory = models.CharField(max_length=500, blank=True)
    log_file = models.CharField(max_length=500, blank=True)
    cpu_hours = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    memory_peak_gb = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    runtime_seconds = models.PositiveIntegerField(null=True, blank=True)
    exit_code = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.job_id} ({self.get_status_display()})"


class AnalysisResult(models.Model):
    """Results from an analysis job."""

    RESULT_TYPE_CHOICES = [
        ('VCF', 'VCF'), ('BAM', 'BAM'), ('FASTQ', 'FASTQ'),
        ('COUNTS', 'Count Matrix'), ('REPORT', 'Report'),
        ('QC', 'QC Metrics'), ('OTHER', 'Other'),
    ]

    job = models.ForeignKey(AnalysisJob, on_delete=models.CASCADE, related_name='results')
    result_type = models.CharField(max_length=20, choices=RESULT_TYPE_CHOICES)
    file_path = models.CharField(max_length=500)
    file_size_bytes = models.BigIntegerField(null=True, blank=True)
    checksum_md5 = models.CharField(max_length=32, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.job.job_id}: {self.get_result_type_display()}"


class ServiceDelivery(models.Model):
    """Delivery of analysis results."""

    DELIVERY_METHOD_CHOICES = [
        ('STORAGE', 'Shared Storage'), ('DOWNLOAD', 'Download Link'),
        ('EMAIL', 'Email'), ('TRANSFER', 'File Transfer'),
    ]

    service = models.ForeignKey(BioinformaticsService, on_delete=models.CASCADE, related_name='deliveries')
    delivery_method = models.CharField(max_length=50, choices=DELIVERY_METHOD_CHOICES, default='STORAGE')
    delivery_path = models.CharField(max_length=500, blank=True)
    delivery_url = models.URLField(blank=True)
    files_included = models.JSONField(default=list)
    report_file = models.FileField(upload_to='bioinformatics/deliveries/', null=True, blank=True)
    delivered_at = models.DateTimeField(auto_now_add=True)
    delivered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Delivery for {self.service.service_id}"
