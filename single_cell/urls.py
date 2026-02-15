# single_cell/urls.py

from django.urls import path
from . import views

app_name = 'single_cell'

urlpatterns = [
    # Sample Types
    path('types/', views.SampleTypeListView.as_view(), name='sample_type_list'),

    # Single-Cell Samples
    path('samples/', views.SingleCellSampleListView.as_view(), name='sample_list'),
    path('samples/create/', views.SingleCellSampleCreateView.as_view(), name='sample_create'),
    path('samples/<int:pk>/', views.SingleCellSampleDetailView.as_view(), name='sample_detail'),
    path('samples/<int:pk>/edit/', views.SingleCellSampleUpdateView.as_view(), name='sample_update'),

    # Libraries
    path('libraries/', views.SingleCellLibraryListView.as_view(), name='library_list'),
    path('libraries/<int:pk>/', views.SingleCellLibraryDetailView.as_view(), name='library_detail'),

    # Feature Barcodes
    path('barcodes/', views.FeatureBarcodeListView.as_view(), name='barcode_list'),
    path('panels/', views.FeatureBarcodePanelListView.as_view(), name='panel_list'),

    # Analysis Results
    path('samples/<int:pk>/clusters/', views.CellClusterListView.as_view(), name='cluster_list'),
]
