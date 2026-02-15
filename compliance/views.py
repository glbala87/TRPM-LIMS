"""
Views for the Compliance app.

Provides views for managing consent protocols and patient consents.
"""
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, View
)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q

from .models import ConsentProtocol, PatientConsent


class ConsentProtocolListView(LoginRequiredMixin, ListView):
    """List view for consent protocols."""

    model = ConsentProtocol
    template_name = 'compliance/protocol_list.html'
    context_object_name = 'protocols'
    paginate_by = 20

    def get_queryset(self):
        """Filter queryset based on search parameters."""
        queryset = ConsentProtocol.objects.all()

        # Filter by active status
        active = self.request.GET.get('active')
        if active == 'true':
            queryset = queryset.filter(is_active=True)
        elif active == 'false':
            queryset = queryset.filter(is_active=False)

        # Filter by protocol type
        protocol_type = self.request.GET.get('type')
        if protocol_type:
            queryset = queryset.filter(protocol_type=protocol_type)

        # Search by name or IRB number
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(irb_number__icontains=search) |
                Q(description__icontains=search)
            )

        return queryset.order_by('-effective_date', 'name')

    def get_context_data(self, **kwargs):
        """Add protocol type choices to context."""
        context = super().get_context_data(**kwargs)
        context['protocol_types'] = ConsentProtocol.PROTOCOL_TYPE_CHOICES
        return context


class ConsentProtocolDetailView(LoginRequiredMixin, DetailView):
    """Detail view for a consent protocol."""

    model = ConsentProtocol
    template_name = 'compliance/protocol_detail.html'
    context_object_name = 'protocol'

    def get_context_data(self, **kwargs):
        """Add related consents to context."""
        context = super().get_context_data(**kwargs)
        context['recent_consents'] = self.object.patient_consents.select_related(
            'patient'
        ).order_by('-consent_date')[:10]
        context['consent_stats'] = {
            'total': self.object.patient_consents.count(),
            'active': self.object.patient_consents.filter(
                status='CONSENTED', is_active=True
            ).count(),
            'withdrawn': self.object.patient_consents.filter(
                status='WITHDRAWN'
            ).count(),
        }
        return context


class ConsentProtocolCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Create view for consent protocols."""

    model = ConsentProtocol
    template_name = 'compliance/protocol_form.html'
    permission_required = 'compliance.add_consentprotocol'
    fields = [
        'name', 'version', 'protocol_type', 'description',
        'irb_number', 'irb_approval_date', 'irb_expiration_date',
        'effective_date', 'expiration_date', 'is_active',
        'document', 'requires_witness', 'requires_legal_representative',
        'minimum_age'
    ]
    success_url = reverse_lazy('compliance:protocol_list')

    def form_valid(self, form):
        """Set created_by to current user."""
        form.instance.created_by = self.request.user
        messages.success(
            self.request,
            f'Consent protocol "{form.instance.name}" created successfully.'
        )
        return super().form_valid(form)


class ConsentProtocolUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Update view for consent protocols."""

    model = ConsentProtocol
    template_name = 'compliance/protocol_form.html'
    permission_required = 'compliance.change_consentprotocol'
    fields = [
        'name', 'version', 'protocol_type', 'description',
        'irb_number', 'irb_approval_date', 'irb_expiration_date',
        'effective_date', 'expiration_date', 'is_active',
        'document', 'requires_witness', 'requires_legal_representative',
        'minimum_age'
    ]

    def get_success_url(self):
        return reverse('compliance:protocol_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(
            self.request,
            f'Consent protocol "{form.instance.name}" updated successfully.'
        )
        return super().form_valid(form)


class PatientConsentListView(LoginRequiredMixin, ListView):
    """List view for patient consents."""

    model = PatientConsent
    template_name = 'compliance/consent_list.html'
    context_object_name = 'consents'
    paginate_by = 25

    def get_queryset(self):
        """Filter queryset based on search parameters."""
        queryset = PatientConsent.objects.select_related(
            'patient', 'protocol', 'consented_by'
        )

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Filter by active
        active = self.request.GET.get('active')
        if active == 'true':
            queryset = queryset.filter(is_active=True)
        elif active == 'false':
            queryset = queryset.filter(is_active=False)

        # Filter by protocol
        protocol_id = self.request.GET.get('protocol')
        if protocol_id:
            queryset = queryset.filter(protocol_id=protocol_id)

        # Search by patient name or OP_NO
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(patient__first_name__icontains=search) |
                Q(patient__last_name__icontains=search) |
                Q(patient__OP_NO__icontains=search)
            )

        return queryset.order_by('-consent_date', '-created_at')

    def get_context_data(self, **kwargs):
        """Add filter options to context."""
        context = super().get_context_data(**kwargs)
        context['status_choices'] = PatientConsent.CONSENT_STATUS_CHOICES
        context['protocols'] = ConsentProtocol.objects.filter(is_active=True)
        return context


class PatientConsentDetailView(LoginRequiredMixin, DetailView):
    """Detail view for a patient consent."""

    model = PatientConsent
    template_name = 'compliance/consent_detail.html'
    context_object_name = 'consent'

    def get_queryset(self):
        return PatientConsent.objects.select_related(
            'patient', 'protocol', 'consented_by', 'withdrawn_by'
        )


class PatientConsentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Create view for patient consents."""

    model = PatientConsent
    template_name = 'compliance/consent_form.html'
    permission_required = 'compliance.add_patientconsent'
    fields = [
        'patient', 'protocol', 'status', 'consent_method',
        'witness_name', 'representative_name', 'representative_relationship',
        'signed_document', 'notes'
    ]
    success_url = reverse_lazy('compliance:consent_list')

    def get_context_data(self, **kwargs):
        """Add active protocols to context."""
        context = super().get_context_data(**kwargs)
        context['active_protocols'] = ConsentProtocol.get_active_protocols()
        return context

    def form_valid(self, form):
        """Set consented_by if consent is given."""
        if form.instance.status == 'CONSENTED':
            form.instance.consented_by = self.request.user
            form.instance.consent_date = timezone.now()
            form.instance.is_active = True
        messages.success(
            self.request,
            'Patient consent record created successfully.'
        )
        return super().form_valid(form)


class GiveConsentView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """View to record that consent was given."""

    permission_required = 'compliance.change_patientconsent'

    def post(self, request, pk):
        """Process consent submission."""
        consent = get_object_or_404(PatientConsent, pk=pk)

        if consent.status != 'PENDING':
            messages.error(
                request,
                'This consent has already been processed.'
            )
            return redirect('compliance:consent_detail', pk=pk)

        # Get form data
        method = request.POST.get('consent_method', 'IN_PERSON')
        witness_name = request.POST.get('witness_name', '')
        representative_name = request.POST.get('representative_name', '')
        representative_relationship = request.POST.get('representative_relationship', '')

        # Give consent
        consent.give_consent(
            consented_by=request.user,
            method=method,
            witness_name=witness_name,
            representative_name=representative_name,
            representative_relationship=representative_relationship
        )

        messages.success(
            request,
            f'Consent recorded successfully for {consent.patient}.'
        )
        return redirect('compliance:consent_detail', pk=pk)


class WithdrawConsentView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """View to record consent withdrawal."""

    permission_required = 'compliance.change_patientconsent'

    def post(self, request, pk):
        """Process consent withdrawal."""
        consent = get_object_or_404(PatientConsent, pk=pk)

        if consent.status != 'CONSENTED':
            messages.error(
                request,
                'Only active consents can be withdrawn.'
            )
            return redirect('compliance:consent_detail', pk=pk)

        reason = request.POST.get('withdrawal_reason', '')

        consent.withdraw_consent(
            withdrawn_by=request.user,
            reason=reason
        )

        messages.success(
            request,
            f'Consent withdrawal recorded for {consent.patient}.'
        )
        return redirect('compliance:consent_detail', pk=pk)


class PatientConsentHistoryView(LoginRequiredMixin, ListView):
    """View consent history for a specific patient."""

    model = PatientConsent
    template_name = 'compliance/patient_consent_history.html'
    context_object_name = 'consents'

    def get_queryset(self):
        """Get consents for the specified patient."""
        from lab_management.models import Patient
        self.patient = get_object_or_404(Patient, pk=self.kwargs['patient_id'])
        return PatientConsent.objects.filter(
            patient=self.patient
        ).select_related('protocol', 'consented_by').order_by('-consent_date')

    def get_context_data(self, **kwargs):
        """Add patient to context."""
        context = super().get_context_data(**kwargs)
        context['patient'] = self.patient
        context['active_consents'] = PatientConsent.get_active_consents_for_patient(
            self.patient
        )
        return context


class CreatePatientConsentView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Create a new consent record for a specific patient."""

    model = PatientConsent
    template_name = 'compliance/patient_consent_form.html'
    permission_required = 'compliance.add_patientconsent'
    fields = [
        'protocol', 'consent_method', 'witness_name',
        'representative_name', 'representative_relationship',
        'signed_document', 'notes'
    ]

    def dispatch(self, request, *args, **kwargs):
        """Get the patient from URL."""
        from lab_management.models import Patient
        self.patient = get_object_or_404(Patient, pk=kwargs['patient_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add patient and active protocols to context."""
        context = super().get_context_data(**kwargs)
        context['patient'] = self.patient
        context['active_protocols'] = ConsentProtocol.get_active_protocols()
        return context

    def form_valid(self, form):
        """Set patient and consent details."""
        form.instance.patient = self.patient
        form.instance.consented_by = self.request.user
        form.instance.consent_date = timezone.now()
        form.instance.status = 'CONSENTED'
        form.instance.is_active = True

        messages.success(
            self.request,
            f'Consent recorded for {self.patient}.'
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'compliance:patient_consent_history',
            kwargs={'patient_id': self.patient.pk}
        )


# API-style views for AJAX operations

def check_consent_status(request, patient_id, protocol_id):
    """
    Check if a patient has valid consent for a specific protocol.

    Returns JSON response with consent status.
    """
    from lab_management.models import Patient

    try:
        patient = Patient.objects.get(pk=patient_id)
        protocol = ConsentProtocol.objects.get(pk=protocol_id)
    except (Patient.DoesNotExist, ConsentProtocol.DoesNotExist):
        return JsonResponse({
            'error': 'Patient or protocol not found',
            'has_consent': False
        }, status=404)

    has_consent = PatientConsent.has_valid_consent(patient, protocol)

    # Get the most recent consent record if exists
    recent_consent = PatientConsent.objects.filter(
        patient=patient,
        protocol=protocol
    ).order_by('-consent_date').first()

    response_data = {
        'has_consent': has_consent,
        'patient_id': patient_id,
        'patient_name': str(patient),
        'protocol_id': protocol_id,
        'protocol_name': str(protocol),
    }

    if recent_consent:
        response_data.update({
            'consent_id': recent_consent.pk,
            'consent_status': recent_consent.status,
            'consent_date': recent_consent.consent_date.isoformat() if recent_consent.consent_date else None,
            'is_active': recent_consent.is_active,
        })

    return JsonResponse(response_data)


def get_active_protocols(request):
    """
    Get all currently active consent protocols.

    Returns JSON list of active protocols.
    """
    protocols = ConsentProtocol.get_active_protocols()

    data = [{
        'id': p.pk,
        'name': p.name,
        'version': p.version,
        'type': p.protocol_type,
        'type_display': p.get_protocol_type_display(),
        'effective_date': p.effective_date.isoformat(),
        'irb_number': p.irb_number,
        'requires_witness': p.requires_witness,
    } for p in protocols]

    return JsonResponse({'protocols': data})
