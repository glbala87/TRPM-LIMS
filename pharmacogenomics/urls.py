# pharmacogenomics/urls.py
"""
URL configuration for pharmacogenomics module.
"""

from django.urls import path
from . import views

app_name = 'pharmacogenomics'

urlpatterns = [
    # Gene views
    path('genes/', views.PGxGeneDashboardView.as_view(), name='gene-dashboard'),
    path('genes/<int:pk>/', views.PGxGeneDetailView.as_view(), name='gene-detail'),

    # Drug views
    path('drugs/', views.DrugListView.as_view(), name='drug-list'),
    path('drugs/<int:pk>/', views.DrugDetailView.as_view(), name='drug-detail'),

    # Panel views
    path('panels/', views.PGxPanelListView.as_view(), name='panel-list'),

    # Result views
    path('results/', views.PGxResultListView.as_view(), name='result-list'),
    path('results/<int:pk>/', views.PGxResultDetailView.as_view(), name='result-detail'),
]
