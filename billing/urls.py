# billing/urls.py

from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # Dashboard
    path('', views.BillingDashboardView.as_view(), name='dashboard'),

    # Price Lists
    path('price-lists/', views.PriceListListView.as_view(), name='pricelist_list'),
    path('price-lists/<int:pk>/', views.PriceListDetailView.as_view(), name='pricelist_detail'),

    # Clients
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/create/', views.ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/', views.ClientDetailView.as_view(), name='client_detail'),
    path('clients/<int:pk>/edit/', views.ClientUpdateView.as_view(), name='client_update'),

    # Invoices
    path('invoices/', views.InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/create/', views.InvoiceCreateView.as_view(), name='invoice_create'),
    path('invoices/<int:pk>/', views.InvoiceDetailView.as_view(), name='invoice_detail'),
    path('invoices/<int:pk>/edit/', views.InvoiceUpdateView.as_view(), name='invoice_update'),
    path('invoices/<int:pk>/send/', views.send_invoice, name='invoice_send'),
    path('invoices/<int:pk>/pdf/', views.invoice_pdf, name='invoice_pdf'),

    # Payments
    path('invoices/<int:pk>/payments/add/', views.PaymentCreateView.as_view(), name='payment_add'),
    path('payments/', views.PaymentListView.as_view(), name='payment_list'),

    # Quotations
    path('quotes/', views.QuotationListView.as_view(), name='quote_list'),
    path('quotes/create/', views.QuotationCreateView.as_view(), name='quote_create'),
    path('quotes/<int:pk>/', views.QuotationDetailView.as_view(), name='quote_detail'),
    path('quotes/<int:pk>/convert/', views.convert_quote_to_invoice, name='quote_convert'),
]
