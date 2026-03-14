# storage/urls.py

from django.urls import path
from . import views

app_name = 'storage'

urlpatterns = [
    # Storage Units
    path('', views.StorageUnitListView.as_view(), name='unit_list'),
    path('<int:pk>/', views.StorageUnitDetailView.as_view(), name='unit_detail'),
    path('create/', views.StorageUnitCreateView.as_view(), name='unit_create'),
    path('<int:pk>/edit/', views.StorageUnitUpdateView.as_view(), name='unit_update'),

    # Racks
    path('rack/<int:pk>/', views.StorageRackDetailView.as_view(), name='rack_detail'),
    path('rack/create/', views.StorageRackCreateView.as_view(), name='rack_create'),
    path('rack/<int:pk>/edit/', views.StorageRackUpdateView.as_view(), name='rack_update'),

    # Logs
    path('logs/', views.StorageLogListView.as_view(), name='log_list'),
]
