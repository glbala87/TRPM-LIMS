# microbiology/views.py

from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from .models import MicrobiologySample, Organism, Antibiotic, ASTPanel, OrganismResult, ASTResult


class CultureListView(LoginRequiredMixin, ListView):
    model = MicrobiologySample
    template_name = 'microbiology/culture_list.html'
    context_object_name = 'cultures'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get('q')
        if search:
            qs = qs.filter(
                Q(sample_id__icontains=search) |
                Q(patient_name__icontains=search)
            )
        return qs.order_by('-created_at')


class CultureDetailView(LoginRequiredMixin, DetailView):
    model = MicrobiologySample
    template_name = 'microbiology/culture_detail.html'
    context_object_name = 'culture'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organism_results'] = OrganismResult.objects.filter(
            sample=self.object
        ).select_related('organism')
        context['ast_results'] = ASTResult.objects.filter(
            organism_result__sample=self.object
        ).select_related('antibiotic', 'organism_result')
        return context


class OrganismListView(LoginRequiredMixin, ListView):
    model = Organism
    template_name = 'microbiology/organism_list.html'
    context_object_name = 'organisms'
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get('q')
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search)
            )
        return qs.order_by('name')


class AntibioticListView(LoginRequiredMixin, ListView):
    model = Antibiotic
    template_name = 'microbiology/antibiotic_list.html'
    context_object_name = 'antibiotics'

    def get_queryset(self):
        return super().get_queryset().select_related('antibiotic_class').order_by('name')


class ASTPanelListView(LoginRequiredMixin, ListView):
    model = ASTPanel
    template_name = 'microbiology/panel_list.html'
    context_object_name = 'panels'


class ASTPanelDetailView(LoginRequiredMixin, DetailView):
    model = ASTPanel
    template_name = 'microbiology/panel_detail.html'
    context_object_name = 'panel'
