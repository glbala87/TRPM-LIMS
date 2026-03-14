# equipment/urls.py

from django.urls import path
from . import views

app_name = 'equipment'

urlpatterns = [
    # Instruments
    path('', views.InstrumentListView.as_view(), name='instrument_list'),
    path('<int:pk>/', views.InstrumentDetailView.as_view(), name='instrument_detail'),
    path('create/', views.InstrumentCreateView.as_view(), name='instrument_create'),
    path('<int:pk>/edit/', views.InstrumentUpdateView.as_view(), name='instrument_update'),
    path('<int:pk>/delete/', views.InstrumentDeleteView.as_view(), name='instrument_delete'),

    # Instrument Types
    path('types/', views.InstrumentTypeListView.as_view(), name='instrument_type_list'),
    path('types/create/', views.InstrumentTypeCreateView.as_view(), name='instrument_type_create'),
    path('types/<int:pk>/edit/', views.InstrumentTypeUpdateView.as_view(), name='instrument_type_update'),

    # Maintenance Records
    path('maintenance/', views.MaintenanceListView.as_view(), name='maintenance_list'),
    path('maintenance/<int:pk>/', views.MaintenanceDetailView.as_view(), name='maintenance_detail'),
    path('maintenance/create/', views.MaintenanceCreateView.as_view(), name='maintenance_create'),
    path('maintenance/<int:pk>/edit/', views.MaintenanceUpdateView.as_view(), name='maintenance_update'),
    path('maintenance/<int:pk>/delete/', views.MaintenanceDeleteView.as_view(), name='maintenance_delete'),
]
