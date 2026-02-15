# bioinformatics/urls.py

from django.urls import path
from . import views

app_name = 'bioinformatics'

urlpatterns = [
    # Pipelines
    path('pipelines/', views.PipelineListView.as_view(), name='pipeline_list'),
    path('pipelines/<int:pk>/', views.PipelineDetailView.as_view(), name='pipeline_detail'),

    # Service Requests
    path('services/', views.BioinformaticsServiceListView.as_view(), name='service_list'),
    path('services/create/', views.BioinformaticsServiceCreateView.as_view(), name='service_create'),
    path('services/<int:pk>/', views.BioinformaticsServiceDetailView.as_view(), name='service_detail'),
    path('services/<int:pk>/approve/', views.approve_service, name='service_approve'),

    # Jobs
    path('jobs/', views.AnalysisJobListView.as_view(), name='job_list'),
    path('jobs/<int:pk>/', views.AnalysisJobDetailView.as_view(), name='job_detail'),

    # Results
    path('results/<int:pk>/', views.AnalysisResultDetailView.as_view(), name='result_detail'),

    # Deliveries
    path('services/<int:pk>/deliver/', views.ServiceDeliveryCreateView.as_view(), name='delivery_create'),
]
