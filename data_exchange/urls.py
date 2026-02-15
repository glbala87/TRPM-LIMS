# data_exchange/urls.py

from django.urls import path
from . import views

app_name = 'data_exchange'

urlpatterns = [
    # Import views
    path('imports/', views.ImportListView.as_view(), name='import_list'),
    path('imports/create/', views.ImportCreateView.as_view(), name='import_create'),
    path('imports/<int:pk>/', views.ImportDetailView.as_view(), name='import_detail'),
    path('imports/<int:pk>/preview/', views.import_preview, name='import_preview'),
    path('imports/<int:pk>/confirm/', views.import_confirm, name='import_confirm'),
    path('imports/<int:pk>/cancel/', views.import_cancel, name='import_cancel'),

    # Export views
    path('exports/', views.ExportListView.as_view(), name='export_list'),
    path('exports/create/', views.ExportCreateView.as_view(), name='export_create'),
    path('exports/<int:pk>/', views.ExportDetailView.as_view(), name='export_detail'),
    path('exports/<int:pk>/download/', views.export_download, name='export_download'),

    # Export templates
    path('templates/', views.ExportTemplateListView.as_view(), name='export_template_list'),
    path('templates/create/', views.ExportTemplateCreateView.as_view(), name='export_template_create'),
    path('templates/<int:pk>/edit/', views.ExportTemplateUpdateView.as_view(), name='export_template_edit'),
    path('templates/<int:pk>/run/', views.export_template_run, name='export_template_run'),

    # API endpoints
    path('api/import/validate/', views.api_validate_import, name='api_validate_import'),
    path('api/export/preview/', views.api_export_preview, name='api_export_preview'),
]
