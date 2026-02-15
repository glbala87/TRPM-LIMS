# tenants/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Organization, Laboratory, LaboratoryMembership


class OrganizationListView(LoginRequiredMixin, ListView):
    model = Organization
    template_name = 'tenants/organization_list.html'
    context_object_name = 'organizations'

    def get_queryset(self):
        # Only show organizations user is a member of
        return Organization.objects.filter(
            memberships__user=self.request.user,
            memberships__is_active=True
        ).distinct()


class OrganizationDetailView(LoginRequiredMixin, DetailView):
    model = Organization
    template_name = 'tenants/organization_detail.html'
    context_object_name = 'organization'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['laboratories'] = self.object.laboratories.filter(is_active=True)
        return context


class LaboratoryListView(LoginRequiredMixin, ListView):
    model = Laboratory
    template_name = 'tenants/laboratory_list.html'
    context_object_name = 'laboratories'

    def get_queryset(self):
        # Only show laboratories user is a member of
        return Laboratory.objects.filter(
            memberships__user=self.request.user,
            memberships__is_active=True
        ).select_related('organization')


class LaboratoryDetailView(LoginRequiredMixin, DetailView):
    model = Laboratory
    template_name = 'tenants/laboratory_detail.html'
    context_object_name = 'laboratory'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['members'] = self.object.memberships.filter(is_active=True).select_related('user')
        return context


@login_required
def switch_laboratory(request, laboratory_id):
    """Switch the current active laboratory context."""
    laboratory = get_object_or_404(Laboratory, pk=laboratory_id, is_active=True)

    # Verify user is a member
    membership = LaboratoryMembership.objects.filter(
        user=request.user,
        laboratory=laboratory,
        is_active=True
    ).first()

    if not membership:
        messages.error(request, "You don't have access to this laboratory.")
        return redirect('tenants:laboratory_list')

    # Set session
    request.session['current_laboratory_id'] = laboratory.id
    request.session['current_organization_id'] = laboratory.organization.id

    messages.success(request, f"Switched to {laboratory.name}")
    return redirect('home')
