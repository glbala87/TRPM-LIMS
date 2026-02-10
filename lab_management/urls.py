from django.urls import path
from lab_management import views

urlpatterns = [
    # Patients/Registration
    path('patients/register/', views.patient_registration, name='patient_registration'),
    path('patients/', views.patient_list, name='patient_list'),  # This already handles both the list and search functionality

    # Lab Orders
    path('lab_orders/', views.lab_orders, name='lab_orders'),
    path('lab-order/', views.lab_order_view, name='lab_order_view'),  # Added URL for the lab order form

    # Test Results
    path('results/', views.results_entry_view, name='results_entry_view'),
    
    # Autocomplete for Patient search by OP_NO, first name, or last name
    path('patients/autocomplete/', views.patient_autocomplete, name='patient_autocomplete'),  # New URL for autocomplete
]
