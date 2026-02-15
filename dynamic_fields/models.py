# dynamic_fields/models.py
"""
Dynamic field creation system.
Inspired by open-lims template system and NanoLIMS custom fields.
"""

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class FieldCategory(models.Model):
    """Category for organizing custom fields."""

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Field Category"
        verbose_name_plural = "Field Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class CustomFieldDefinition(models.Model):
    """Definition of a custom field."""

    FIELD_TYPE_CHOICES = [
        ('TEXT', 'Text (single line)'),
        ('TEXTAREA', 'Text (multi-line)'),
        ('INTEGER', 'Integer'),
        ('DECIMAL', 'Decimal'),
        ('BOOLEAN', 'Yes/No'),
        ('DATE', 'Date'),
        ('DATETIME', 'Date & Time'),
        ('SELECT', 'Dropdown Selection'),
        ('MULTISELECT', 'Multiple Selection'),
        ('FILE', 'File Upload'),
        ('URL', 'URL Link'),
        ('EMAIL', 'Email'),
        ('PHONE', 'Phone Number'),
        ('JSON', 'JSON Data'),
    ]

    # Target model (what entity this field attaches to)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE,
        help_text="The model this field applies to"
    )

    # Field definition
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, help_text="Internal field code (no spaces)")
    field_type = models.CharField(max_length=20, choices=FIELD_TYPE_CHOICES, default='TEXT')
    category = models.ForeignKey(FieldCategory, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    help_text = models.CharField(max_length=500, blank=True)

    # Validation
    is_required = models.BooleanField(default=False)
    min_value = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True)
    max_value = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True)
    max_length = models.PositiveIntegerField(null=True, blank=True)
    regex_pattern = models.CharField(max_length=500, blank=True, help_text="Validation regex pattern")
    default_value = models.TextField(blank=True)

    # For SELECT/MULTISELECT types
    choices = models.JSONField(
        default=list, blank=True,
        help_text="List of {value, label} choices"
    )

    # Display
    order = models.PositiveIntegerField(default=0)
    show_in_list = models.BooleanField(default=False, help_text="Show in list/table views")
    show_in_form = models.BooleanField(default=True)
    is_searchable = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Custom Field Definition"
        verbose_name_plural = "Custom Field Definitions"
        ordering = ['content_type', 'order', 'name']
        unique_together = [['content_type', 'code']]

    def __str__(self):
        return f"{self.content_type.model}: {self.name}"


class CustomFieldValue(models.Model):
    """Value of a custom field for a specific object."""

    field_definition = models.ForeignKey(
        CustomFieldDefinition, on_delete=models.CASCADE, related_name='values'
    )

    # Generic relation to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Value storage (use appropriate field based on field_type)
    value_text = models.TextField(blank=True)
    value_integer = models.BigIntegerField(null=True, blank=True)
    value_decimal = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True)
    value_boolean = models.BooleanField(null=True)
    value_date = models.DateField(null=True, blank=True)
    value_datetime = models.DateTimeField(null=True, blank=True)
    value_json = models.JSONField(null=True, blank=True)
    value_file = models.FileField(upload_to='custom_fields/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Custom Field Value"
        verbose_name_plural = "Custom Field Values"
        unique_together = [['field_definition', 'content_type', 'object_id']]
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['field_definition']),
        ]

    def __str__(self):
        return f"{self.field_definition.name}: {self.get_value()}"

    def get_value(self):
        """Get the value based on field type."""
        field_type = self.field_definition.field_type
        if field_type in ['TEXT', 'TEXTAREA', 'URL', 'EMAIL', 'PHONE']:
            return self.value_text
        elif field_type == 'INTEGER':
            return self.value_integer
        elif field_type == 'DECIMAL':
            return self.value_decimal
        elif field_type == 'BOOLEAN':
            return self.value_boolean
        elif field_type == 'DATE':
            return self.value_date
        elif field_type == 'DATETIME':
            return self.value_datetime
        elif field_type in ['SELECT', 'MULTISELECT', 'JSON']:
            return self.value_json
        elif field_type == 'FILE':
            return self.value_file
        return None

    def set_value(self, value):
        """Set the value based on field type."""
        field_type = self.field_definition.field_type
        if field_type in ['TEXT', 'TEXTAREA', 'URL', 'EMAIL', 'PHONE']:
            self.value_text = str(value) if value else ''
        elif field_type == 'INTEGER':
            self.value_integer = int(value) if value else None
        elif field_type == 'DECIMAL':
            self.value_decimal = value
        elif field_type == 'BOOLEAN':
            self.value_boolean = bool(value)
        elif field_type == 'DATE':
            self.value_date = value
        elif field_type == 'DATETIME':
            self.value_datetime = value
        elif field_type in ['SELECT', 'MULTISELECT', 'JSON']:
            self.value_json = value
        elif field_type == 'FILE':
            self.value_file = value


class FieldTemplate(models.Model):
    """Template defining a set of custom fields for a use case."""

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    fields = models.ManyToManyField(CustomFieldDefinition, through='FieldTemplateField')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Field Template"
        ordering = ['name']

    def __str__(self):
        return self.name


class FieldTemplateField(models.Model):
    """Link between template and field with ordering."""

    template = models.ForeignKey(FieldTemplate, on_delete=models.CASCADE)
    field = models.ForeignKey(CustomFieldDefinition, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=False, help_text="Override field required setting")

    class Meta:
        ordering = ['order']
        unique_together = [['template', 'field']]
