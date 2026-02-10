# molecular_diagnostics/urls.py

from django.urls import path
from . import views

app_name = 'molecular_diagnostics'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Sample views
    path('samples/', views.sample_list, name='sample_list'),
    path('samples/<int:pk>/', views.sample_detail, name='sample_detail'),

    # Workflow transitions
    path('samples/<int:pk>/transition/', views.sample_transition, name='sample_transition'),

    # Reports
    path('reports/<int:pk>/generate/', views.generate_report, name='generate_report'),
    path('reports/<int:pk>/download/', views.download_report, name='download_report'),

    # Plate management
    path('plates/', views.plate_list, name='plate_list'),
    path('plates/<int:pk>/', views.plate_detail, name='plate_detail'),
    path('plates/<int:pk>/layout/', views.plate_layout, name='plate_layout'),

    # TAT monitoring
    path('tat/', views.tat_dashboard, name='tat_dashboard'),
    path('tat/at-risk/', views.at_risk_samples, name='at_risk_samples'),
]
