# storage/views.py

from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q

from .models import StorageUnit, StorageRack, StoragePosition, StorageLog
from .forms import StorageUnitForm, StorageRackForm, StorageLogForm


# --- Storage Unit Views ---

class StorageUnitListView(LoginRequiredMixin, ListView):
    model = StorageUnit
    template_name = 'storage/unit_list.html'
    context_object_name = 'units'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        unit_type = self.request.GET.get('type')
        if unit_type:
            qs = qs.filter(unit_type=unit_type)
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        search = self.request.GET.get('q')
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(code__icontains=search) |
                Q(location__icontains=search)
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type_choices'] = StorageUnit.UNIT_TYPE_CHOICES
        context['status_choices'] = StorageUnit.STATUS_CHOICES
        return context


class StorageUnitDetailView(LoginRequiredMixin, DetailView):
    model = StorageUnit
    template_name = 'storage/unit_detail.html'
    context_object_name = 'unit'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['racks'] = self.object.racks.all()
        return context


class StorageUnitCreateView(LoginRequiredMixin, CreateView):
    model = StorageUnit
    form_class = StorageUnitForm
    template_name = 'storage/unit_form.html'
    success_url = reverse_lazy('storage:unit_list')


class StorageUnitUpdateView(LoginRequiredMixin, UpdateView):
    model = StorageUnit
    form_class = StorageUnitForm
    template_name = 'storage/unit_form.html'
    success_url = reverse_lazy('storage:unit_list')


# --- Storage Rack Views ---

class StorageRackDetailView(LoginRequiredMixin, DetailView):
    model = StorageRack
    template_name = 'storage/rack_detail.html'
    context_object_name = 'rack'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['positions'] = self.object.positions.all()
        return context


class StorageRackCreateView(LoginRequiredMixin, CreateView):
    model = StorageRack
    form_class = StorageRackForm
    template_name = 'storage/rack_form.html'

    def get_success_url(self):
        return reverse_lazy('storage:unit_detail', kwargs={'pk': self.object.unit.pk})


class StorageRackUpdateView(LoginRequiredMixin, UpdateView):
    model = StorageRack
    form_class = StorageRackForm
    template_name = 'storage/rack_form.html'

    def get_success_url(self):
        return reverse_lazy('storage:unit_detail', kwargs={'pk': self.object.unit.pk})


# --- Storage Log Views ---

class StorageLogListView(LoginRequiredMixin, ListView):
    model = StorageLog
    template_name = 'storage/log_list.html'
    context_object_name = 'logs'
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset().select_related('position', 'performed_by')
        action = self.request.GET.get('action')
        if action:
            qs = qs.filter(action=action)
        search = self.request.GET.get('q')
        if search:
            qs = qs.filter(sample_id__icontains=search)
        return qs
