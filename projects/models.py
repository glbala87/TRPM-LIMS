# projects/models.py
"""
Project-based organization models.
Inspired by baobab.lims project management and miso-lims project structure.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class ProjectCategory(models.Model):
    """Category/type of project."""

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Project Category"
        verbose_name_plural = "Project Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Project(models.Model):
    """Research or clinical project."""

    STATUS_CHOICES = [
        ('DRAFT', 'Draft'), ('PENDING_APPROVAL', 'Pending Approval'),
        ('ACTIVE', 'Active'), ('ON_HOLD', 'On Hold'),
        ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled'),
        ('ARCHIVED', 'Archived'),
    ]

    project_id = models.CharField(max_length=50, unique=True, editable=False)
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)

    category = models.ForeignKey(ProjectCategory, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')

    # Dates
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # People
    principal_investigator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='pi_projects'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_projects'
    )

    # Ethics & Compliance
    ethics_approval_number = models.CharField(max_length=100, blank=True)
    ethics_approval_date = models.DateField(null=True, blank=True)
    ethics_expiry_date = models.DateField(null=True, blank=True)
    ethics_document = models.FileField(upload_to='projects/ethics/', null=True, blank=True)
    consent_required = models.BooleanField(default=True)
    consent_form = models.FileField(upload_to='projects/consent/', null=True, blank=True)

    # Funding
    funding_source = models.CharField(max_length=200, blank=True)
    grant_number = models.CharField(max_length=100, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    # Targets
    target_sample_count = models.PositiveIntegerField(null=True, blank=True)
    target_participant_count = models.PositiveIntegerField(null=True, blank=True)

    # Settings
    settings = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Project"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.project_id:
            self.project_id = f"PRJ-{timezone.now().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.project_id}: {self.name}"

    @property
    def sample_count(self):
        return self.samples.count()

    @property
    def is_ethics_valid(self):
        if not self.ethics_expiry_date:
            return True
        return self.ethics_expiry_date >= timezone.now().date()


class ProjectMember(models.Model):
    """Member/participant of a project."""

    ROLE_CHOICES = [
        ('PI', 'Principal Investigator'), ('CO_PI', 'Co-Investigator'),
        ('RESEARCHER', 'Researcher'), ('TECHNICIAN', 'Lab Technician'),
        ('COORDINATOR', 'Project Coordinator'), ('ANALYST', 'Data Analyst'),
        ('VIEWER', 'Viewer'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='RESEARCHER')

    can_add_samples = models.BooleanField(default=True)
    can_edit_samples = models.BooleanField(default=True)
    can_view_results = models.BooleanField(default=True)
    can_manage_members = models.BooleanField(default=False)

    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Project Member"
        unique_together = [['project', 'user']]

    def __str__(self):
        return f"{self.user} - {self.project.short_name or self.project.name} ({self.get_role_display()})"


class ProjectSample(models.Model):
    """Sample associated with a project."""

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='samples')
    molecular_sample = models.ForeignKey(
        'molecular_diagnostics.MolecularSample', on_delete=models.CASCADE, related_name='project_associations'
    )
    external_sample_id = models.CharField(max_length=100, blank=True, help_text="External/collaborator sample ID")
    subject_id = models.CharField(max_length=100, blank=True, help_text="Study subject identifier")

    consent_obtained = models.BooleanField(default=False)
    consent_date = models.DateField(null=True, blank=True)
    consent_version = models.CharField(max_length=50, blank=True)

    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Project Sample"
        unique_together = [['project', 'molecular_sample']]

    def __str__(self):
        return f"{self.project.project_id}: {self.molecular_sample.sample_id}"


class ProjectMilestone(models.Model):
    """Project milestone/deliverable."""

    STATUS_CHOICES = [
        ('PENDING', 'Pending'), ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'), ('DELAYED', 'Delayed'), ('CANCELLED', 'Cancelled'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Project Milestone"
        ordering = ['project', 'order', 'target_date']

    def __str__(self):
        return f"{self.project.short_name}: {self.name}"


class ProjectDocument(models.Model):
    """Documents associated with a project."""

    DOCUMENT_TYPE_CHOICES = [
        ('PROTOCOL', 'Protocol'), ('ETHICS', 'Ethics Document'),
        ('CONSENT', 'Consent Form'), ('SOP', 'SOP'),
        ('REPORT', 'Report'), ('OTHER', 'Other'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, default='OTHER')
    file = models.FileField(upload_to='projects/documents/')
    version = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Project Document"
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.project.project_id}: {self.title}"
