# dynamic_fields/views.py

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
import json
from .models import (
    FieldCategory, CustomFieldDefinition, CustomFieldValue,
    FieldTemplate, FieldTemplateField
)


class FieldCategoryListView(LoginRequiredMixin, ListView):
    model = FieldCategory
    template_name = 'dynamic_fields/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return FieldCategory.objects.filter(is_active=True).order_by('order', 'name')


class CustomFieldDefinitionListView(LoginRequiredMixin, ListView):
    model = CustomFieldDefinition
    template_name = 'dynamic_fields/field_list.html'
    context_object_name = 'fields'

    def get_queryset(self):
        queryset = CustomFieldDefinition.objects.filter(is_active=True).select_related(
            'content_type', 'category'
        )

        content_type = self.request.GET.get('model')
        if content_type:
            queryset = queryset.filter(content_type_id=content_type)

        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)

        return queryset.order_by('content_type', 'order', 'name')


class CustomFieldDefinitionDetailView(LoginRequiredMixin, DetailView):
    model = CustomFieldDefinition
    template_name = 'dynamic_fields/field_detail.html'
    context_object_name = 'field'


class CustomFieldDefinitionCreateView(LoginRequiredMixin, CreateView):
    model = CustomFieldDefinition
    template_name = 'dynamic_fields/field_form.html'
    fields = [
        'content_type', 'name', 'code', 'field_type', 'category',
        'description', 'help_text', 'is_required', 'min_value', 'max_value',
        'max_length', 'regex_pattern', 'default_value', 'choices',
        'order', 'show_in_list', 'show_in_form', 'is_searchable'
    ]
    success_url = reverse_lazy('dynamic_fields:field_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class CustomFieldDefinitionUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomFieldDefinition
    template_name = 'dynamic_fields/field_form.html'
    fields = [
        'name', 'description', 'help_text', 'is_required',
        'min_value', 'max_value', 'max_length', 'regex_pattern',
        'default_value', 'choices', 'order', 'show_in_list',
        'show_in_form', 'is_searchable', 'is_active'
    ]

    def get_success_url(self):
        return reverse_lazy('dynamic_fields:field_detail', kwargs={'pk': self.object.pk})


class FieldTemplateListView(LoginRequiredMixin, ListView):
    model = FieldTemplate
    template_name = 'dynamic_fields/template_list.html'
    context_object_name = 'templates'

    def get_queryset(self):
        return FieldTemplate.objects.filter(is_active=True).select_related('content_type')


class FieldTemplateDetailView(LoginRequiredMixin, DetailView):
    model = FieldTemplate
    template_name = 'dynamic_fields/template_detail.html'
    context_object_name = 'template'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['template_fields'] = FieldTemplateField.objects.filter(
            template=self.object
        ).select_related('field').order_by('order')
        return context


class FieldTemplateCreateView(LoginRequiredMixin, CreateView):
    model = FieldTemplate
    template_name = 'dynamic_fields/template_form.html'
    fields = ['name', 'code', 'description', 'content_type']
    success_url = reverse_lazy('dynamic_fields:template_list')


@login_required
def get_field_values(request, model, object_id):
    """Get custom field values for an object."""
    try:
        content_type = ContentType.objects.get(model=model.lower())
    except ContentType.DoesNotExist:
        return JsonResponse({'error': 'Invalid model'}, status=400)

    # Get field definitions for this model
    field_definitions = CustomFieldDefinition.objects.filter(
        content_type=content_type,
        is_active=True,
        show_in_form=True
    ).order_by('order')

    # Get existing values
    existing_values = {
        v.field_definition_id: v
        for v in CustomFieldValue.objects.filter(
            content_type=content_type,
            object_id=object_id
        )
    }

    fields_data = []
    for field_def in field_definitions:
        value_obj = existing_values.get(field_def.id)
        fields_data.append({
            'id': field_def.id,
            'name': field_def.name,
            'code': field_def.code,
            'field_type': field_def.field_type,
            'is_required': field_def.is_required,
            'help_text': field_def.help_text,
            'choices': field_def.choices,
            'value': value_obj.get_value() if value_obj else field_def.default_value or None
        })

    return JsonResponse({'fields': fields_data})


@login_required
@require_POST
def save_field_values(request, model, object_id):
    """Save custom field values for an object."""
    try:
        content_type = ContentType.objects.get(model=model.lower())
    except ContentType.DoesNotExist:
        return JsonResponse({'error': 'Invalid model'}, status=400)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    for field_id, value in data.items():
        try:
            field_def = CustomFieldDefinition.objects.get(
                id=field_id,
                content_type=content_type,
                is_active=True
            )
        except CustomFieldDefinition.DoesNotExist:
            continue

        # Get or create value
        field_value, created = CustomFieldValue.objects.get_or_create(
            field_definition=field_def,
            content_type=content_type,
            object_id=object_id,
            defaults={'updated_by': request.user}
        )

        field_value.set_value(value)
        field_value.updated_by = request.user
        field_value.save()

    return JsonResponse({'status': 'success'})
