# molecular_diagnostics/models/batches.py

from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class InstrumentRun(models.Model):
    """Represents a single run on a laboratory instrument"""

    RUN_STATUS_CHOICES = [
        ('PLANNED', 'Planned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]

    run_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False
    )
    instrument = models.ForeignKey(
        'equipment.Instrument',
        on_delete=models.PROTECT,
        related_name='runs'
    )
    run_date = models.DateTimeField(default=timezone.now)
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='instrument_runs'
    )
    status = models.CharField(
        max_length=20,
        choices=RUN_STATUS_CHOICES,
        default='PLANNED'
    )

    protocol_name = models.CharField(max_length=200, blank=True)
    protocol_version = models.CharField(max_length=50, blank=True)

    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)
    run_parameters = models.JSONField(
        default=dict,
        blank=True,
        help_text="Instrument-specific run parameters"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Instrument Run"
        verbose_name_plural = "Instrument Runs"
        ordering = ['-run_date']

    def save(self, *args, **kwargs):
        if not self.run_id:
            date_str = timezone.now().strftime('%Y%m%d')
            unique_suffix = uuid.uuid4().hex[:6].upper()
            self.run_id = f"RUN-{date_str}-{unique_suffix}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.run_id} - {self.instrument.name} ({self.get_status_display()})"

    @property
    def duration_hours(self):
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds() / 3600
        return None


class PCRPlate(models.Model):
    """PCR plate for organizing samples"""

    PLATE_TYPE_CHOICES = [
        ('96', '96-well'),
        ('384', '384-well'),
    ]

    barcode = models.CharField(max_length=100, unique=True)
    plate_type = models.CharField(
        max_length=10,
        choices=PLATE_TYPE_CHOICES,
        default='96'
    )
    name = models.CharField(max_length=200, blank=True)

    instrument_run = models.ForeignKey(
        InstrumentRun,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='plates'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "PCR Plate"
        verbose_name_plural = "PCR Plates"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.barcode} ({self.get_plate_type_display()})"

    @property
    def well_count(self):
        return int(self.plate_type)

    @property
    def rows(self):
        return 8 if self.plate_type == '96' else 16

    @property
    def columns(self):
        return 12 if self.plate_type == '96' else 24

    def get_layout(self):
        """Return plate layout as a dictionary"""
        layout = {}
        for well in self.wells.all():
            layout[well.position] = well
        return layout


class PlateWell(models.Model):
    """Individual well in a PCR plate"""

    CONTROL_TYPE_CHOICES = [
        ('', 'Sample'),
        ('POSITIVE', 'Positive Control'),
        ('NEGATIVE', 'Negative Control'),
        ('NTC', 'No Template Control'),
        ('CALIBRATOR', 'Calibrator'),
        ('EMPTY', 'Empty'),
    ]

    plate = models.ForeignKey(
        PCRPlate,
        on_delete=models.CASCADE,
        related_name='wells'
    )
    position = models.CharField(
        max_length=4,
        help_text="Well position (e.g., A1, H12)"
    )
    sample = models.ForeignKey(
        'molecular_diagnostics.MolecularSample',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='plate_wells'
    )
    control_type = models.CharField(
        max_length=20,
        choices=CONTROL_TYPE_CHOICES,
        blank=True,
        default=''
    )
    control_sample = models.ForeignKey(
        'molecular_diagnostics.ControlSample',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='plate_wells'
    )

    replicate_number = models.PositiveIntegerField(
        default=1,
        help_text="Replicate number for duplicate/triplicate testing"
    )

    class Meta:
        verbose_name = "Plate Well"
        verbose_name_plural = "Plate Wells"
        unique_together = [['plate', 'position']]
        ordering = ['plate', 'position']

    def __str__(self):
        content = self.sample.sample_id if self.sample else self.get_control_type_display()
        return f"{self.plate.barcode}:{self.position} - {content}"

    @property
    def row(self):
        return self.position[0]

    @property
    def column(self):
        return int(self.position[1:])

    @property
    def is_control(self):
        return bool(self.control_type)


class NGSLibrary(models.Model):
    """NGS library preparation tracking"""

    library_id = models.CharField(max_length=50, unique=True)
    sample = models.ForeignKey(
        'molecular_diagnostics.MolecularSample',
        on_delete=models.CASCADE,
        related_name='ngs_libraries'
    )

    index_sequence = models.CharField(
        max_length=50,
        help_text="Index/barcode sequence"
    )
    index_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Index kit name/ID"
    )

    concentration_ng_ul = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    fragment_size_bp = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Average fragment size in base pairs"
    )
    molarity_nm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Library molarity in nM"
    )

    prep_date = models.DateField(default=timezone.now)
    prep_kit = models.ForeignKey(
        'reagents.MolecularReagent',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='libraries_prepared'
    )
    prepared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    qc_passed = models.BooleanField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "NGS Library"
        verbose_name_plural = "NGS Libraries"
        ordering = ['-prep_date']

    def __str__(self):
        return f"{self.library_id} - {self.sample.sample_id}"


class NGSPool(models.Model):
    """Pool of NGS libraries for sequencing"""

    pool_id = models.CharField(max_length=50, unique=True)
    libraries = models.ManyToManyField(
        NGSLibrary,
        related_name='pools'
    )

    concentration_ng_ul = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    molarity_nm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    volume_ul = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    pool_date = models.DateField(default=timezone.now)
    pooled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    instrument_run = models.ForeignKey(
        InstrumentRun,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ngs_pools'
    )

    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "NGS Pool"
        verbose_name_plural = "NGS Pools"
        ordering = ['-pool_date']

    def __str__(self):
        return f"{self.pool_id} ({self.libraries.count()} libraries)"

    @property
    def library_count(self):
        return self.libraries.count()
