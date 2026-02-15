"""
Serializers for dynamic_fields app models.
"""
from rest_framework import serializers
from dynamic_fields.models import (
    FieldCategory, CustomFieldDefinition, CustomFieldValue,
    FieldTemplate, FieldTemplateField
)


class FieldCategorySerializer(serializers.ModelSerializer):
    """Serializer for FieldCategory model."""

    class Meta:
        model = FieldCategory
        fields = ['id', 'code', 'name', 'description', 'order', 'is_active']


class CustomFieldDefinitionSerializer(serializers.ModelSerializer):
    """Serializer for CustomFieldDefinition model."""
    field_type_display = serializers.CharField(source='get_field_type_display', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    model_name = serializers.CharField(source='content_type.model', read_only=True)

    class Meta:
        model = CustomFieldDefinition
        fields = [
            'id', 'content_type', 'model_name', 'name', 'code',
            'field_type', 'field_type_display', 'category', 'category_name',
            'description', 'help_text',
            'is_required', 'min_value', 'max_value', 'max_length',
            'regex_pattern', 'default_value', 'choices',
            'order', 'show_in_list', 'show_in_form', 'is_searchable',
            'is_active', 'created_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at']


class CustomFieldDefinitionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for CustomFieldDefinition list views."""
    field_type_display = serializers.CharField(source='get_field_type_display', read_only=True)
    model_name = serializers.CharField(source='content_type.model', read_only=True)

    class Meta:
        model = CustomFieldDefinition
        fields = ['id', 'code', 'name', 'model_name', 'field_type_display', 'is_required', 'is_active']


class CustomFieldValueSerializer(serializers.ModelSerializer):
    """Serializer for CustomFieldValue model."""
    field_name = serializers.CharField(source='field_definition.name', read_only=True)
    field_code = serializers.CharField(source='field_definition.code', read_only=True)
    value = serializers.SerializerMethodField()

    class Meta:
        model = CustomFieldValue
        fields = [
            'id', 'field_definition', 'field_name', 'field_code',
            'content_type', 'object_id', 'value',
            'created_at', 'updated_at', 'updated_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_value(self, obj):
        return obj.get_value()


class FieldTemplateFieldSerializer(serializers.ModelSerializer):
    """Serializer for FieldTemplateField model."""
    field_name = serializers.CharField(source='field.name', read_only=True)
    field_code = serializers.CharField(source='field.code', read_only=True)

    class Meta:
        model = FieldTemplateField
        fields = ['id', 'template', 'field', 'field_name', 'field_code', 'order', 'is_required']


class FieldTemplateSerializer(serializers.ModelSerializer):
    """Serializer for FieldTemplate model."""
    model_name = serializers.CharField(source='content_type.model', read_only=True)
    template_fields = serializers.SerializerMethodField()

    class Meta:
        model = FieldTemplate
        fields = [
            'id', 'code', 'name', 'description', 'content_type', 'model_name',
            'template_fields', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_template_fields(self, obj):
        template_fields = FieldTemplateField.objects.filter(template=obj).select_related('field')
        return FieldTemplateFieldSerializer(template_fields, many=True).data
