# dynamic_fields/urls.py

from django.urls import path
from . import views

app_name = 'dynamic_fields'

urlpatterns = [
    # Field Categories
    path('categories/', views.FieldCategoryListView.as_view(), name='category_list'),

    # Field Definitions
    path('fields/', views.CustomFieldDefinitionListView.as_view(), name='field_list'),
    path('fields/create/', views.CustomFieldDefinitionCreateView.as_view(), name='field_create'),
    path('fields/<int:pk>/', views.CustomFieldDefinitionDetailView.as_view(), name='field_detail'),
    path('fields/<int:pk>/edit/', views.CustomFieldDefinitionUpdateView.as_view(), name='field_update'),

    # Templates
    path('templates/', views.FieldTemplateListView.as_view(), name='template_list'),
    path('templates/create/', views.FieldTemplateCreateView.as_view(), name='template_create'),
    path('templates/<int:pk>/', views.FieldTemplateDetailView.as_view(), name='template_detail'),

    # API for getting field values
    path('api/values/<str:model>/<int:object_id>/', views.get_field_values, name='api_get_values'),
    path('api/values/<str:model>/<int:object_id>/save/', views.save_field_values, name='api_save_values'),
]
