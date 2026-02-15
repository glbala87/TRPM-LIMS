# bioinformatics/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from .models import (
    Pipeline, PipelineParameter, BioinformaticsService,
    AnalysisJob, AnalysisResult, ServiceDelivery
)


class PipelineListView(LoginRequiredMixin, ListView):
    model = Pipeline
    template_name = 'bioinformatics/pipeline_list.html'
    context_object_name = 'pipelines'

    def get_queryset(self):
        return Pipeline.objects.filter(is_active=True)


class PipelineDetailView(LoginRequiredMixin, DetailView):
    model = Pipeline
    template_name = 'bioinformatics/pipeline_detail.html'
    context_object_name = 'pipeline'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['parameters'] = self.object.parameters.all()
        return context


class BioinformaticsServiceListView(LoginRequiredMixin, ListView):
    model = BioinformaticsService
    template_name = 'bioinformatics/service_list.html'
    context_object_name = 'services'
    paginate_by = 25

    def get_queryset(self):
        queryset = BioinformaticsService.objects.select_related(
            'pipeline', 'requested_by', 'assigned_to'
        ).order_by('-requested_at')

        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        return queryset


class BioinformaticsServiceDetailView(LoginRequiredMixin, DetailView):
    model = BioinformaticsService
    template_name = 'bioinformatics/service_detail.html'
    context_object_name = 'service'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['jobs'] = self.object.jobs.all()
        context['deliveries'] = self.object.deliveries.all()
        return context


class BioinformaticsServiceCreateView(LoginRequiredMixin, CreateView):
    model = BioinformaticsService
    template_name = 'bioinformatics/service_form.html'
    fields = ['pipeline', 'title', 'description', 'priority', 'samples', 'parameters']
    success_url = reverse_lazy('bioinformatics:service_list')

    def form_valid(self, form):
        form.instance.requested_by = self.request.user
        return super().form_valid(form)


@login_required
def approve_service(request, pk):
    service = get_object_or_404(BioinformaticsService, pk=pk)

    if service.status != 'REQUESTED':
        messages.error(request, "This service cannot be approved.")
        return redirect('bioinformatics:service_detail', pk=pk)

    service.status = 'APPROVED'
    service.approved_by = request.user
    service.approved_at = timezone.now()
    service.save()

    messages.success(request, f"Service {service.service_id} approved.")
    return redirect('bioinformatics:service_detail', pk=pk)


class AnalysisJobListView(LoginRequiredMixin, ListView):
    model = AnalysisJob
    template_name = 'bioinformatics/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 25

    def get_queryset(self):
        queryset = AnalysisJob.objects.select_related('service', 'sample')

        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by('-created_at')


class AnalysisJobDetailView(LoginRequiredMixin, DetailView):
    model = AnalysisJob
    template_name = 'bioinformatics/job_detail.html'
    context_object_name = 'job'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['results'] = self.object.results.all()
        return context


class AnalysisResultDetailView(LoginRequiredMixin, DetailView):
    model = AnalysisResult
    template_name = 'bioinformatics/result_detail.html'
    context_object_name = 'result'


class ServiceDeliveryCreateView(LoginRequiredMixin, CreateView):
    model = ServiceDelivery
    template_name = 'bioinformatics/delivery_form.html'
    fields = ['delivery_method', 'delivery_path', 'delivery_url', 'files_included', 'notes']

    def form_valid(self, form):
        service = get_object_or_404(BioinformaticsService, pk=self.kwargs['pk'])
        form.instance.service = service
        form.instance.delivered_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('bioinformatics:service_detail', kwargs={'pk': self.kwargs['pk']})
