# pathology/urls.py

from django.urls import path
from . import views

app_name = 'pathology'

urlpatterns = [
    path('', views.CaseListView.as_view(), name='case_list'),
    path('case/<int:pk>/', views.CaseDetailView.as_view(), name='case_detail'),
    path('histology/', views.HistologyListView.as_view(), name='histology_list'),
    path('histology/<int:pk>/', views.HistologyDetailView.as_view(), name='histology_detail'),
]
