# microbiology/urls.py

from django.urls import path
from . import views

app_name = 'microbiology'

urlpatterns = [
    path('', views.CultureListView.as_view(), name='culture_list'),
    path('culture/<int:pk>/', views.CultureDetailView.as_view(), name='culture_detail'),
    path('organisms/', views.OrganismListView.as_view(), name='organism_list'),
    path('antibiotics/', views.AntibioticListView.as_view(), name='antibiotic_list'),
    path('panels/', views.ASTPanelListView.as_view(), name='panel_list'),
    path('panels/<int:pk>/', views.ASTPanelDetailView.as_view(), name='panel_detail'),
]
