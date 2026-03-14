# pathology/views.py

from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from .models import Pathology, PathologyAddendum, Histology, HistologyBlock, HistologySlide


class CaseListView(LoginRequiredMixin, ListView):
    model = Pathology
    template_name = 'pathology/case_list.html'
    context_object_name = 'cases'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get('q')
        if search:
            qs = qs.filter(
                Q(accession_number__icontains=search) |
                Q(patient_name__icontains=search)
            )
        return qs.order_by('-created_at')


class CaseDetailView(LoginRequiredMixin, DetailView):
    model = Pathology
    template_name = 'pathology/case_detail.html'
    context_object_name = 'case'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['addenda'] = PathologyAddendum.objects.filter(pathology=self.object)
        return context


class HistologyListView(LoginRequiredMixin, ListView):
    model = Histology
    template_name = 'pathology/histology_list.html'
    context_object_name = 'specimens'
    paginate_by = 25

    def get_queryset(self):
        return super().get_queryset().order_by('-created_at')


class HistologyDetailView(LoginRequiredMixin, DetailView):
    model = Histology
    template_name = 'pathology/histology_detail.html'
    context_object_name = 'specimen'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blocks'] = HistologyBlock.objects.filter(histology=self.object)
        context['slides'] = HistologySlide.objects.filter(block__histology=self.object)
        return context
