# billing/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.utils import timezone
from .models import (
    PriceList, ServicePrice, Client,
    Invoice, InvoiceItem, Payment, QuotationRequest
)


class BillingDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'billing/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Summary stats
        context['pending_invoices'] = Invoice.objects.filter(status='PENDING').count()
        context['overdue_invoices'] = Invoice.objects.filter(status='OVERDUE').count()
        context['total_outstanding'] = sum(
            i.balance_due for i in Invoice.objects.exclude(status__in=['PAID', 'CANCELLED'])
        )

        # Recent invoices
        context['recent_invoices'] = Invoice.objects.select_related('client').order_by('-invoice_date')[:10]

        # Recent payments
        context['recent_payments'] = Payment.objects.select_related('invoice__client').order_by('-payment_date')[:10]

        return context


class PriceListListView(LoginRequiredMixin, ListView):
    model = PriceList
    template_name = 'billing/pricelist_list.html'
    context_object_name = 'price_lists'

    def get_queryset(self):
        return PriceList.objects.filter(is_active=True).order_by('-effective_from')


class PriceListDetailView(LoginRequiredMixin, DetailView):
    model = PriceList
    template_name = 'billing/pricelist_detail.html'
    context_object_name = 'price_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prices'] = self.object.prices.filter(is_active=True).order_by('service_name')
        return context


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'billing/client_list.html'
    context_object_name = 'clients'
    paginate_by = 25

    def get_queryset(self):
        queryset = Client.objects.all()

        client_type = self.request.GET.get('type')
        if client_type:
            queryset = queryset.filter(client_type=client_type)

        active_only = self.request.GET.get('active')
        if active_only == '1':
            queryset = queryset.filter(is_active=True)

        return queryset.order_by('name')


class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'billing/client_detail.html'
    context_object_name = 'client'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoices'] = self.object.invoices.order_by('-invoice_date')[:10]
        context['quotes'] = self.object.quotes.order_by('-quote_date')[:5]
        return context


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    template_name = 'billing/client_form.html'
    fields = [
        'name', 'client_type', 'contact_name', 'email', 'phone',
        'address', 'city', 'country', 'tax_id', 'price_list',
        'payment_terms', 'credit_limit', 'discount_percent', 'notes'
    ]
    success_url = reverse_lazy('billing:client_list')


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    template_name = 'billing/client_form.html'
    fields = [
        'name', 'client_type', 'contact_name', 'email', 'phone',
        'address', 'city', 'country', 'tax_id', 'price_list',
        'payment_terms', 'credit_limit', 'discount_percent', 'is_active', 'notes'
    ]

    def get_success_url(self):
        return reverse_lazy('billing:client_detail', kwargs={'pk': self.object.pk})


class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'billing/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 25

    def get_queryset(self):
        queryset = Invoice.objects.select_related('client')

        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by('-invoice_date')


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = 'billing/invoice_detail.html'
    context_object_name = 'invoice'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all()
        context['payments'] = self.object.payments.order_by('-payment_date')
        return context


class InvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    template_name = 'billing/invoice_form.html'
    fields = [
        'client', 'price_list', 'due_date', 'discount_amount',
        'tax_rate', 'billing_address', 'notes'
    ]
    success_url = reverse_lazy('billing:invoice_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class InvoiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Invoice
    template_name = 'billing/invoice_form.html'
    fields = [
        'due_date', 'discount_amount', 'tax_rate',
        'billing_address', 'notes', 'internal_notes'
    ]

    def get_success_url(self):
        return reverse_lazy('billing:invoice_detail', kwargs={'pk': self.object.pk})


@login_required
def send_invoice(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)

    if invoice.status not in ['DRAFT', 'PENDING']:
        messages.error(request, "This invoice cannot be sent.")
        return redirect('billing:invoice_detail', pk=pk)

    invoice.status = 'SENT'
    invoice.sent_date = timezone.now().date()
    invoice.save()

    # TODO: Send email notification to client

    messages.success(request, f"Invoice {invoice.invoice_number} marked as sent.")
    return redirect('billing:invoice_detail', pk=pk)


@login_required
def invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)

    # TODO: Generate PDF
    # For now, return a placeholder response
    return HttpResponse(
        f"PDF generation for invoice {invoice.invoice_number} - To be implemented",
        content_type='text/plain'
    )


class PaymentCreateView(LoginRequiredMixin, CreateView):
    model = Payment
    template_name = 'billing/payment_form.html'
    fields = ['amount', 'payment_method', 'payment_date', 'reference_number', 'notes']

    def form_valid(self, form):
        invoice = get_object_or_404(Invoice, pk=self.kwargs['pk'])
        form.instance.invoice = invoice
        form.instance.received_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('billing:invoice_detail', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoice'] = get_object_or_404(Invoice, pk=self.kwargs.get('pk'))
        return context


class PaymentListView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'billing/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 50

    def get_queryset(self):
        return Payment.objects.select_related('invoice__client').order_by('-payment_date')


class QuotationListView(LoginRequiredMixin, ListView):
    model = QuotationRequest
    template_name = 'billing/quote_list.html'
    context_object_name = 'quotes'
    paginate_by = 25

    def get_queryset(self):
        queryset = QuotationRequest.objects.select_related('client')

        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by('-quote_date')


class QuotationDetailView(LoginRequiredMixin, DetailView):
    model = QuotationRequest
    template_name = 'billing/quote_detail.html'
    context_object_name = 'quote'


class QuotationCreateView(LoginRequiredMixin, CreateView):
    model = QuotationRequest
    template_name = 'billing/quote_form.html'
    fields = [
        'client', 'valid_until', 'discount_amount',
        'terms_and_conditions', 'notes'
    ]
    success_url = reverse_lazy('billing:quote_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


@login_required
def convert_quote_to_invoice(request, pk):
    quote = get_object_or_404(QuotationRequest, pk=pk)

    if quote.status != 'ACCEPTED':
        messages.error(request, "Only accepted quotations can be converted to invoices.")
        return redirect('billing:quote_detail', pk=pk)

    if quote.converted_to_invoice:
        messages.error(request, "This quotation has already been converted.")
        return redirect('billing:invoice_detail', pk=quote.converted_to_invoice.pk)

    # Create invoice from quote
    invoice = Invoice.objects.create(
        client=quote.client,
        price_list=quote.client.price_list or PriceList.objects.filter(is_default=True).first(),
        due_date=timezone.now().date() + timezone.timedelta(days=30),
        subtotal=quote.subtotal,
        discount_amount=quote.discount_amount,
        total_amount=quote.total_amount,
        notes=quote.notes,
        created_by=request.user
    )

    quote.converted_to_invoice = invoice
    quote.save()

    messages.success(request, f"Created invoice {invoice.invoice_number} from quotation.")
    return redirect('billing:invoice_detail', pk=invoice.pk)
