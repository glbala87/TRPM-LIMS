"""
URL configuration for the Compliance app.

Provides URL patterns for consent management views.
"""
from django.urls import path
from . import views

app_name = 'compliance'

urlpatterns = [
    # Consent Protocol URLs
    path(
        'protocols/',
        views.ConsentProtocolListView.as_view(),
        name='protocol_list'
    ),
    path(
        'protocols/<int:pk>/',
        views.ConsentProtocolDetailView.as_view(),
        name='protocol_detail'
    ),
    path(
        'protocols/create/',
        views.ConsentProtocolCreateView.as_view(),
        name='protocol_create'
    ),
    path(
        'protocols/<int:pk>/update/',
        views.ConsentProtocolUpdateView.as_view(),
        name='protocol_update'
    ),

    # Patient Consent URLs
    path(
        'consents/',
        views.PatientConsentListView.as_view(),
        name='consent_list'
    ),
    path(
        'consents/<int:pk>/',
        views.PatientConsentDetailView.as_view(),
        name='consent_detail'
    ),
    path(
        'consents/create/',
        views.PatientConsentCreateView.as_view(),
        name='consent_create'
    ),
    path(
        'consents/<int:pk>/give/',
        views.GiveConsentView.as_view(),
        name='give_consent'
    ),
    path(
        'consents/<int:pk>/withdraw/',
        views.WithdrawConsentView.as_view(),
        name='withdraw_consent'
    ),

    # Patient-specific consent views
    path(
        'patient/<int:patient_id>/consents/',
        views.PatientConsentHistoryView.as_view(),
        name='patient_consent_history'
    ),
    path(
        'patient/<int:patient_id>/consent/new/',
        views.CreatePatientConsentView.as_view(),
        name='create_patient_consent'
    ),

    # API-style endpoints for AJAX operations
    path(
        'api/check-consent/<int:patient_id>/<int:protocol_id>/',
        views.check_consent_status,
        name='check_consent_status'
    ),
    path(
        'api/active-protocols/',
        views.get_active_protocols,
        name='get_active_protocols'
    ),
]
