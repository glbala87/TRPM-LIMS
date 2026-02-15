# transfers/urls.py

from django.urls import path
from . import views

app_name = 'transfers'

urlpatterns = [
    # Transfer list and CRUD
    path('', views.transfer_list, name='transfer_list'),
    path('create/', views.transfer_create, name='transfer_create'),
    path('quick-create/', views.transfer_quick_create, name='transfer_quick_create'),
    path('<str:transfer_number>/', views.transfer_detail, name='transfer_detail'),
    path('<str:transfer_number>/edit/', views.transfer_edit, name='transfer_edit'),

    # Transfer actions
    path('<str:transfer_number>/dispatch/', views.transfer_dispatch, name='transfer_dispatch'),
    path('<str:transfer_number>/receive/', views.transfer_receive, name='transfer_receive'),
    path('<str:transfer_number>/cancel/', views.transfer_cancel, name='transfer_cancel'),
    path('<str:transfer_number>/tracking/', views.transfer_tracking, name='transfer_tracking'),

    # Sample history
    path('sample/<str:sample_id>/history/', views.sample_movement_history, name='sample_movement_history'),

    # Dashboard views
    path('dashboard/active/', views.active_transfers, name='active_transfers'),
    path('dashboard/statistics/', views.transfer_statistics, name='transfer_statistics'),

    # API endpoints
    path('api/status/<str:transfer_number>/', views.api_transfer_status, name='api_transfer_status'),
    path('api/sample/<str:sample_id>/history/', views.api_sample_history, name='api_sample_history'),
    path(
        'api/<str:transfer_number>/sample/<str:sample_id>/discrepancy/',
        views.api_report_discrepancy,
        name='api_report_discrepancy'
    ),
]
