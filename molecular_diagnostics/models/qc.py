# molecular_diagnostics/models/qc.py

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class QCMetricDefinition(models.Model):
    """Definition of a QC metric with acceptable ranges"""

    METRIC_TYPE_CHOICES = [
        ('NUMERIC', 'Numeric'),
        ('PERCENTAGE', 'Percentage'),
        ('BOOLEAN', 'Pass/Fail'),
        ('RANGE', 'Within Range'),
    ]

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    metric_type = models.CharField(
        max_length=20,
        choices=METRIC_TYPE_CHOICES,
        default='NUMERIC'
    )

    unit = models.CharField(max_length=50, blank=True)

    min_acceptable = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Minimum acceptable value"
    )
    max_acceptable = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Maximum acceptable value"
    )
    target_value = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Target/optimal value"
    )

    warning_min = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Warning threshold (lower)"
    )
    warning_max = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Warning threshold (upper)"
    )

    applicable_test_types = models.JSONField(
        default=list,
        blank=True,
        help_text="List of test types this metric applies to"
    )

    is_critical = models.BooleanField(
        default=False,
        help_text="If true, failure of this metric fails the entire QC"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "QC Metric Definition"
        verbose_name_plural = "QC Metric Definitions"
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"

    def evaluate(self, value):
        """Evaluate if a value passes this QC metric"""
        if self.metric_type == 'BOOLEAN':
            return bool(value)

        if value is None:
            return None

        try:
            value = float(value)
        except (TypeError, ValueError):
            return False

        if self.min_acceptable is not None and value < float(self.min_acceptable):
            return False
        if self.max_acceptable is not None and value > float(self.max_acceptable):
            return False
        return True

    def get_warning_status(self, value):
        """Check if value is in warning range but still passing"""
        if not self.evaluate(value):
            return 'FAIL'

        if value is None:
            return None

        try:
            value = float(value)
        except (TypeError, ValueError):
            return None

        if self.warning_min is not None and value < float(self.warning_min):
            return 'WARNING'
        if self.warning_max is not None and value > float(self.warning_max):
            return 'WARNING'
        return 'PASS'


class ControlSample(models.Model):
    """Control samples used for QC validation"""

    CONTROL_TYPE_CHOICES = [
        ('POSITIVE', 'Positive Control'),
        ('NEGATIVE', 'Negative Control'),
        ('NTC', 'No Template Control'),
        ('CALIBRATOR', 'Calibrator'),
        ('REFERENCE', 'Reference Material'),
    ]

    name = models.CharField(max_length=100)
    control_type = models.CharField(max_length=20, choices=CONTROL_TYPE_CHOICES)
    lot_number = models.CharField(max_length=50, blank=True)

    expected_result = models.CharField(
        max_length=200,
        help_text="Expected result for this control"
    )
    expected_value_min = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True
    )
    expected_value_max = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True
    )

    target_gene = models.ForeignKey(
        'molecular_diagnostics.GeneTarget',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='control_samples'
    )
    test_panel = models.ForeignKey(
        'molecular_diagnostics.MolecularTestPanel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='control_samples'
    )

    expiration_date = models.DateField(null=True, blank=True)
    storage_temperature = models.CharField(max_length=50, blank=True)

    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Control Sample"
        verbose_name_plural = "Control Samples"
        ordering = ['control_type', 'name']

    def __str__(self):
        return f"{self.get_control_type_display()}: {self.name}"

    @property
    def is_expired(self):
        if self.expiration_date:
            return self.expiration_date < timezone.now().date()
        return False


class QCRecord(models.Model):
    """Record of QC results for a run or plate"""

    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('PASSED', 'Passed'),
        ('FAILED', 'Failed'),
        ('WARNING', 'Passed with Warnings'),
    ]

    instrument_run = models.ForeignKey(
        'molecular_diagnostics.InstrumentRun',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='qc_records'
    )
    pcr_plate = models.ForeignKey(
        'molecular_diagnostics.PCRPlate',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='qc_records'
    )

    metric = models.ForeignKey(
        QCMetricDefinition,
        on_delete=models.PROTECT,
        related_name='records'
    )
    control_sample = models.ForeignKey(
        ControlSample,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='qc_records'
    )

    value = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True
    )
    value_text = models.CharField(
        max_length=200,
        blank=True,
        help_text="For non-numeric results"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    passed = models.BooleanField(null=True, blank=True)

    recorded_at = models.DateTimeField(default=timezone.now)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recorded_qc'
    )

    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_qc'
    )

    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "QC Record"
        verbose_name_plural = "QC Records"
        ordering = ['-recorded_at']

    def __str__(self):
        entity = self.instrument_run or self.pcr_plate
        return f"{entity}: {self.metric.name} = {self.value or self.value_text}"

    def save(self, *args, **kwargs):
        # Auto-evaluate pass/fail based on metric definition
        if self.value is not None and self.passed is None:
            self.passed = self.metric.evaluate(self.value)
            warning_status = self.metric.get_warning_status(self.value)
            if warning_status == 'FAIL':
                self.status = 'FAILED'
            elif warning_status == 'WARNING':
                self.status = 'WARNING'
            elif warning_status == 'PASS':
                self.status = 'PASSED'
        super().save(*args, **kwargs)
