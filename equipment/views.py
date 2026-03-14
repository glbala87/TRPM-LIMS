# equipment/views.py

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Count, Q
from django.utils import timezone

from .models import InstrumentType, Instrument, MaintenanceRecord
from .forms import InstrumentTypeForm, InstrumentForm, MaintenanceRecordForm


# --- Instrument Views ---

class InstrumentListView(LoginRequiredMixin, ListView):
    model = Instrument
    template_name = 'equipment/instrument_list.html'
    context_object_name = 'instruments'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().select_related('instrument_type')
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        search = self.request.GET.get('q')
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(serial_number__icontains=search) |
                Q(manufacturer__icontains=search)
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Instrument.STATUS_CHOICES
        context['current_status'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('q', '')
        today = timezone.now().date()
        context['maintenance_due_count'] = Instrument.objects.filter(
            next_maintenance__lte=today, is_active=True
        ).count()
        context['calibration_due_count'] = Instrument.objects.filter(
            next_calibration__lte=today, is_active=True
        ).count()
        return context


class InstrumentDetailView(LoginRequiredMixin, DetailView):
    model = Instrument
    template_name = 'equipment/instrument_detail.html'
    context_object_name = 'instrument'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['maintenance_records'] = self.object.maintenance_records.all()[:10]
        return context


class InstrumentCreateView(LoginRequiredMixin, CreateView):
    model = Instrument
    form_class = InstrumentForm
    template_name = 'equipment/instrument_form.html'
    success_url = reverse_lazy('equipment:instrument_list')


class InstrumentUpdateView(LoginRequiredMixin, UpdateView):
    model = Instrument
    form_class = InstrumentForm
    template_name = 'equipment/instrument_form.html'
    success_url = reverse_lazy('equipment:instrument_list')


class InstrumentDeleteView(LoginRequiredMixin, DeleteView):
    model = Instrument
    template_name = 'equipment/instrument_confirm_delete.html'
    success_url = reverse_lazy('equipment:instrument_list')


# --- Instrument Type Views ---

class InstrumentTypeListView(LoginRequiredMixin, ListView):
    model = InstrumentType
    template_name = 'equipment/instrument_type_list.html'
    context_object_name = 'types'

    def get_queryset(self):
        return super().get_queryset().annotate(instrument_count=Count('instruments'))


class InstrumentTypeCreateView(LoginRequiredMixin, CreateView):
    model = InstrumentType
    form_class = InstrumentTypeForm
    template_name = 'equipment/instrument_type_form.html'
    success_url = reverse_lazy('equipment:instrument_type_list')


class InstrumentTypeUpdateView(LoginRequiredMixin, UpdateView):
    model = InstrumentType
    form_class = InstrumentTypeForm
    template_name = 'equipment/instrument_type_form.html'
    success_url = reverse_lazy('equipment:instrument_type_list')


# --- Maintenance Record Views ---

class MaintenanceListView(LoginRequiredMixin, ListView):
    model = MaintenanceRecord
    template_name = 'equipment/maintenance_list.html'
    context_object_name = 'records'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().select_related('instrument')
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        mtype = self.request.GET.get('type')
        if mtype:
            qs = qs.filter(maintenance_type=mtype)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = MaintenanceRecord.STATUS_CHOICES
        context['type_choices'] = MaintenanceRecord.MAINTENANCE_TYPE_CHOICES
        return context


class MaintenanceDetailView(LoginRequiredMixin, DetailView):
    model = MaintenanceRecord
    template_name = 'equipment/maintenance_detail.html'
    context_object_name = 'record'


class MaintenanceCreateView(LoginRequiredMixin, CreateView):
    model = MaintenanceRecord
    form_class = MaintenanceRecordForm
    template_name = 'equipment/maintenance_form.html'
    success_url = reverse_lazy('equipment:maintenance_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class MaintenanceUpdateView(LoginRequiredMixin, UpdateView):
    model = MaintenanceRecord
    form_class = MaintenanceRecordForm
    template_name = 'equipment/maintenance_form.html'
    success_url = reverse_lazy('equipment:maintenance_list')


class MaintenanceDeleteView(LoginRequiredMixin, DeleteView):
    model = MaintenanceRecord
    template_name = 'equipment/maintenance_confirm_delete.html'
    success_url = reverse_lazy('equipment:maintenance_list')
