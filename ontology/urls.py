# ontology/urls.py

from django.urls import path
from . import views

app_name = 'ontology'

urlpatterns = [
    # Ontology Sources
    path('sources/', views.OntologySourceListView.as_view(), name='source_list'),

    # Disease Terms
    path('diseases/', views.DiseaseOntologyListView.as_view(), name='disease_list'),
    path('diseases/<int:pk>/', views.DiseaseOntologyDetailView.as_view(), name='disease_detail'),
    path('diseases/search/', views.disease_search, name='disease_search'),

    # Anatomical Sites
    path('anatomy/', views.AnatomicalSiteListView.as_view(), name='anatomy_list'),

    # Clinical Indications
    path('indications/', views.ClinicalIndicationListView.as_view(), name='indication_list'),
    path('indications/<int:pk>/', views.ClinicalIndicationDetailView.as_view(), name='indication_detail'),

    # Organisms
    path('organisms/', views.OrganismListView.as_view(), name='organism_list'),

    # Patient Diagnoses
    path('diagnoses/', views.PatientDiagnosisListView.as_view(), name='diagnosis_list'),
    path('diagnoses/add/', views.PatientDiagnosisCreateView.as_view(), name='diagnosis_create'),
]
