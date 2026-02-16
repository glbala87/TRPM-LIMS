# pharmacogenomics/views.py
"""
Views for pharmacogenomics module.
"""

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import PGxGene, Drug, PGxResult, PGxPanel
from .services import DiplotypeService, RecommendationService


class PGxGeneDashboardView(LoginRequiredMixin, ListView):
    """Dashboard view showing all PGx genes."""
    model = PGxGene
    template_name = 'pharmacogenomics/gene_dashboard.html'
    context_object_name = 'genes'

    def get_queryset(self):
        return PGxGene.objects.filter(is_active=True).prefetch_related('alleles')


class PGxGeneDetailView(LoginRequiredMixin, DetailView):
    """Detail view for a PGx gene."""
    model = PGxGene
    template_name = 'pharmacogenomics/gene_detail.html'
    context_object_name = 'gene'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['alleles'] = self.object.alleles.filter(is_active=True)
        context['phenotypes'] = self.object.phenotypes.all()
        context['drug_interactions'] = self.object.drug_interactions.filter(
            is_active=True
        ).select_related('drug')
        return context


class DrugListView(LoginRequiredMixin, ListView):
    """List of drugs with PGx interactions."""
    model = Drug
    template_name = 'pharmacogenomics/drug_list.html'
    context_object_name = 'drugs'

    def get_queryset(self):
        return Drug.objects.filter(is_active=True).prefetch_related('gene_interactions')


class DrugDetailView(LoginRequiredMixin, DetailView):
    """Detail view for a drug."""
    model = Drug
    template_name = 'pharmacogenomics/drug_detail.html'
    context_object_name = 'drug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gene_interactions'] = self.object.gene_interactions.filter(
            is_active=True
        ).select_related('gene').prefetch_related('recommendations')
        return context


class PGxResultListView(LoginRequiredMixin, ListView):
    """List of PGx results."""
    model = PGxResult
    template_name = 'pharmacogenomics/result_list.html'
    context_object_name = 'results'
    paginate_by = 25

    def get_queryset(self):
        return PGxResult.objects.select_related(
            'molecular_result__sample',
            'gene',
            'phenotype'
        ).order_by('-created_at')


class PGxResultDetailView(LoginRequiredMixin, DetailView):
    """Detail view for a PGx result."""
    model = PGxResult
    template_name = 'pharmacogenomics/result_detail.html'
    context_object_name = 'result'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['drug_results'] = self.object.drug_results.select_related(
            'drug', 'recommendation'
        )

        # Get recommendation service summary
        service = RecommendationService()
        context['clinical_summary'] = service.generate_clinical_summary(
            self.object.molecular_result
        )
        return context


class PGxPanelListView(LoginRequiredMixin, ListView):
    """List of PGx panels."""
    model = PGxPanel
    template_name = 'pharmacogenomics/panel_list.html'
    context_object_name = 'panels'

    def get_queryset(self):
        return PGxPanel.objects.filter(is_active=True).prefetch_related('genes')
