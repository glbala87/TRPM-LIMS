# single_cell/views.py

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import (
    SingleCellSampleType, SingleCellSample, FeatureBarcode,
    FeatureBarcodePanel, SingleCellLibrary, CellCluster
)


class SampleTypeListView(LoginRequiredMixin, ListView):
    model = SingleCellSampleType
    template_name = 'single_cell/sample_type_list.html'
    context_object_name = 'sample_types'

    def get_queryset(self):
        return SingleCellSampleType.objects.filter(is_active=True)


class SingleCellSampleListView(LoginRequiredMixin, ListView):
    model = SingleCellSample
    template_name = 'single_cell/sample_list.html'
    context_object_name = 'samples'
    paginate_by = 25

    def get_queryset(self):
        queryset = SingleCellSample.objects.select_related(
            'molecular_sample', 'sample_type'
        ).order_by('-created_at')

        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        platform = self.request.GET.get('platform')
        if platform:
            queryset = queryset.filter(platform=platform)

        return queryset


class SingleCellSampleDetailView(LoginRequiredMixin, DetailView):
    model = SingleCellSample
    template_name = 'single_cell/sample_detail.html'
    context_object_name = 'sample'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['libraries'] = self.object.libraries.select_related('ngs_library')
        context['clusters'] = self.object.clusters.all()
        return context


class SingleCellSampleCreateView(LoginRequiredMixin, CreateView):
    model = SingleCellSample
    template_name = 'single_cell/sample_form.html'
    fields = [
        'sample_id', 'molecular_sample', 'sample_type', 'platform',
        'initial_cell_count', 'cell_concentration', 'viability_percent',
        'target_cell_recovery', 'is_nuclei', 'notes'
    ]
    success_url = reverse_lazy('single_cell:sample_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class SingleCellSampleUpdateView(LoginRequiredMixin, UpdateView):
    model = SingleCellSample
    template_name = 'single_cell/sample_form.html'
    fields = [
        'status', 'actual_cell_recovery', 'chip_id', 'chip_position',
        'capture_time', 'mean_reads_per_cell', 'median_genes_per_cell',
        'median_umi_per_cell', 'sequencing_saturation', 'notes'
    ]

    def get_success_url(self):
        return reverse_lazy('single_cell:sample_detail', kwargs={'pk': self.object.pk})


class SingleCellLibraryListView(LoginRequiredMixin, ListView):
    model = SingleCellLibrary
    template_name = 'single_cell/library_list.html'
    context_object_name = 'libraries'
    paginate_by = 25


class SingleCellLibraryDetailView(LoginRequiredMixin, DetailView):
    model = SingleCellLibrary
    template_name = 'single_cell/library_detail.html'
    context_object_name = 'library'


class FeatureBarcodeListView(LoginRequiredMixin, ListView):
    model = FeatureBarcode
    template_name = 'single_cell/barcode_list.html'
    context_object_name = 'barcodes'

    def get_queryset(self):
        return FeatureBarcode.objects.filter(is_active=True)


class FeatureBarcodePanelListView(LoginRequiredMixin, ListView):
    model = FeatureBarcodePanel
    template_name = 'single_cell/panel_list.html'
    context_object_name = 'panels'

    def get_queryset(self):
        return FeatureBarcodePanel.objects.filter(is_active=True).prefetch_related('feature_barcodes')


class CellClusterListView(LoginRequiredMixin, ListView):
    model = CellCluster
    template_name = 'single_cell/cluster_list.html'
    context_object_name = 'clusters'

    def get_queryset(self):
        sample_id = self.kwargs.get('pk')
        return CellCluster.objects.filter(single_cell_sample_id=sample_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sample'] = get_object_or_404(SingleCellSample, pk=self.kwargs.get('pk'))
        return context
