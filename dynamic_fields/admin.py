# dynamic_fields/admin.py

from django.contrib import admin
from .models import (
    FieldCategory, CustomFieldDefinition, CustomFieldValue,
    FieldTemplate, FieldTemplateField
)


@admin.register(FieldCategory)
class FieldCategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['order', 'name']


@admin.register(CustomFieldDefinition)
class CustomFieldDefinitionAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'name', 'content_type', 'field_type', 'category',
        'is_required', 'show_in_list', 'is_active'
    ]
    list_filter = ['content_type', 'field_type', 'category', 'is_required', 'is_active']
    search_fields = ['code', 'name', 'description']
    readonly_fields = ['created_at']
    ordering = ['content_type', 'order', 'name']

    fieldsets = (
        (None, {
            'fields': ('content_type', 'name', 'code', 'field_type', 'category')
        }),
        ('Display', {
            'fields': ('description', 'help_text', 'order')
        }),
        ('Validation', {
            'fields': ('is_required', 'min_value', 'max_value', 'max_length', 'regex_pattern', 'default_value')
        }),
        ('Choices (for SELECT/MULTISELECT)', {
            'fields': ('choices',),
            'classes': ('collapse',)
        }),
        ('Visibility', {
            'fields': ('show_in_list', 'show_in_form', 'is_searchable')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CustomFieldValue)
class CustomFieldValueAdmin(admin.ModelAdmin):
    list_display = ['field_definition', 'content_type', 'object_id', 'get_display_value', 'updated_at']
    list_filter = ['field_definition__field_type', 'content_type']
    search_fields = ['field_definition__name', 'value_text']
    readonly_fields = ['created_at', 'updated_at']

    def get_display_value(self, obj):
        value = obj.get_value()
        if value is None:
            return '-'
        str_val = str(value)
        return str_val[:50] + '...' if len(str_val) > 50 else str_val
    get_display_value.short_description = 'Value'


class FieldTemplateFieldInline(admin.TabularInline):
    model = FieldTemplateField
    extra = 1
    fields = ['field', 'order', 'is_required']


@admin.register(FieldTemplate)
class FieldTemplateAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'content_type', 'field_count', 'is_active']
    list_filter = ['content_type', 'is_active']
    search_fields = ['code', 'name']
    readonly_fields = ['created_at']
    inlines = [FieldTemplateFieldInline]

    def field_count(self, obj):
        return obj.fields.count()
    field_count.short_description = 'Fields'


@admin.register(FieldTemplateField)
class FieldTemplateFieldAdmin(admin.ModelAdmin):
    list_display = ['template', 'field', 'order', 'is_required']
    list_filter = ['template', 'is_required']
    ordering = ['template', 'order']
