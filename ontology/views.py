# ontology/views.py

from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db.models import Q
from django.urls import reverse_lazy
from .models import (
    OntologySource, DiseaseOntology, AnatomicalSite,
    ClinicalIndication, Organism, PatientDiagnosis
)


class OntologySourceListView(LoginRequiredMixin, ListView):
    model = OntologySource
    template_name = 'ontology/source_list.html'
    context_object_name = 'sources'

    def get_queryset(self):
        return OntologySource.objects.filter(is_active=True)


class DiseaseOntologyListView(LoginRequiredMixin, ListView):
    model = DiseaseOntology
    template_name = 'ontology/disease_list.html'
    context_object_name = 'diseases'
    paginate_by = 50

    def get_queryset(self):
        queryset = DiseaseOntology.objects.filter(is_active=True).select_related('source', 'parent')

        source = self.request.GET.get('source')
        if source:
            queryset = queryset.filter(source_id=source)

        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(code__icontains=query) | Q(name__icontains=query)
            )

        return queryset.order_by('source', 'code')


class DiseaseOntologyDetailView(LoginRequiredMixin, DetailView):
    model = DiseaseOntology
    template_name = 'ontology/disease_detail.html'
    context_object_name = 'disease'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['children'] = self.object.children.filter(is_active=True)
        context['indications'] = self.object.indications.filter(is_active=True)
        return context


def disease_search(request):
    """AJAX search for disease terms."""
    query = request.GET.get('q', '')
    source = request.GET.get('source', '')

    if len(query) < 2:
        return JsonResponse({'results': []})

    queryset = DiseaseOntology.objects.filter(is_active=True)

    if source:
        queryset = queryset.filter(source__code=source)

    queryset = queryset.filter(
        Q(code__icontains=query) | Q(name__icontains=query)
    )[:20]

    results = [
        {
            'id': d.id,
            'code': d.code,
            'name': d.name,
            'source': d.source.code,
            'full_code': d.full_code,
        }
        for d in queryset
    ]

    return JsonResponse({'results': results})


class AnatomicalSiteListView(LoginRequiredMixin, ListView):
    model = AnatomicalSite
    template_name = 'ontology/anatomy_list.html'
    context_object_name = 'sites'

    def get_queryset(self):
        queryset = AnatomicalSite.objects.filter(is_active=True)

        system = self.request.GET.get('system')
        if system:
            queryset = queryset.filter(system=system)

        return queryset.order_by('system', 'name')


class ClinicalIndicationListView(LoginRequiredMixin, ListView):
    model = ClinicalIndication
    template_name = 'ontology/indication_list.html'
    context_object_name = 'indications'

    def get_queryset(self):
        return ClinicalIndication.objects.filter(is_active=True).prefetch_related('diseases', 'test_panels')


class ClinicalIndicationDetailView(LoginRequiredMixin, DetailView):
    model = ClinicalIndication
    template_name = 'ontology/indication_detail.html'
    context_object_name = 'indication'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['diseases'] = self.object.diseases.filter(is_active=True)
        context['test_panels'] = self.object.test_panels.filter(is_active=True)
        return context


class OrganismListView(LoginRequiredMixin, ListView):
    model = Organism
    template_name = 'ontology/organism_list.html'
    context_object_name = 'organisms'

    def get_queryset(self):
        queryset = Organism.objects.filter(is_active=True)

        filter_type = self.request.GET.get('type')
        if filter_type == 'host':
            queryset = queryset.filter(is_host=True)
        elif filter_type == 'pathogen':
            queryset = queryset.filter(is_pathogen=True)

        return queryset.order_by('scientific_name')


class PatientDiagnosisListView(LoginRequiredMixin, ListView):
    model = PatientDiagnosis
    template_name = 'ontology/diagnosis_list.html'
    context_object_name = 'diagnoses'
    paginate_by = 25

    def get_queryset(self):
        return PatientDiagnosis.objects.select_related(
            'patient', 'disease', 'anatomical_site'
        ).order_by('-diagnosis_date')


class PatientDiagnosisCreateView(LoginRequiredMixin, CreateView):
    model = PatientDiagnosis
    template_name = 'ontology/diagnosis_form.html'
    fields = [
        'patient', 'disease', 'anatomical_site', 'diagnosis_date',
        'is_primary', 'is_confirmed', 'diagnosed_by', 'notes'
    ]
    success_url = reverse_lazy('ontology:diagnosis_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
