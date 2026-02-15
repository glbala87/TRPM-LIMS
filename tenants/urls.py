# tenants/urls.py

from django.urls import path
from . import views

app_name = 'tenants'

urlpatterns = [
    # Organization views
    path('organizations/', views.OrganizationListView.as_view(), name='organization_list'),
    path('organizations/<int:pk>/', views.OrganizationDetailView.as_view(), name='organization_detail'),

    # Laboratory views
    path('laboratories/', views.LaboratoryListView.as_view(), name='laboratory_list'),
    path('laboratories/<int:pk>/', views.LaboratoryDetailView.as_view(), name='laboratory_detail'),

    # Tenant switching
    path('switch/<int:laboratory_id>/', views.switch_laboratory, name='switch_laboratory'),
]
