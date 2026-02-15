# billing/models.py
"""
Billing and financial management models.
Inspired by beak-lims billing module.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import uuid


class PriceList(models.Model):
    """Price list for services."""

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    currency = models.CharField(max_length=3, default='USD')
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Price List"
        ordering = ['-effective_from']

    def save(self, *args, **kwargs):
        if self.is_default:
            PriceList.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.currency})"


class ServicePrice(models.Model):
    """Price for a specific service/test."""

    price_list = models.ForeignKey(PriceList, on_delete=models.CASCADE, related_name='prices')
    test_panel = models.ForeignKey(
        'molecular_diagnostics.MolecularTestPanel', on_delete=models.CASCADE,
        null=True, blank=True, related_name='prices'
    )
    service_code = models.CharField(max_length=50)
    service_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    min_quantity = models.PositiveIntegerField(default=1)

    # Volume discounts
    volume_discount_enabled = models.BooleanField(default=False)
    volume_discount_tiers = models.JSONField(
        default=list, blank=True,
        help_text="List of {min_qty, discount_percent}"
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Service Price"
        unique_together = [['price_list', 'service_code']]
        ordering = ['service_name']

    def __str__(self):
        return f"{self.service_name}: {self.price_list.currency} {self.unit_price}"


class Client(models.Model):
    """Billing client/customer."""

    CLIENT_TYPE_CHOICES = [
        ('HOSPITAL', 'Hospital'), ('CLINIC', 'Clinic'),
        ('RESEARCH', 'Research Institution'), ('PRIVATE', 'Private Practice'),
        ('INDIVIDUAL', 'Individual'), ('OTHER', 'Other'),
    ]

    PAYMENT_TERMS_CHOICES = [
        ('PREPAID', 'Prepaid'), ('NET15', 'Net 15 Days'),
        ('NET30', 'Net 30 Days'), ('NET45', 'Net 45 Days'),
        ('NET60', 'Net 60 Days'),
    ]

    client_id = models.CharField(max_length=50, unique=True, editable=False)
    name = models.CharField(max_length=200)
    client_type = models.CharField(max_length=20, choices=CLIENT_TYPE_CHOICES, default='CLINIC')

    # Contact
    contact_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)

    # Billing
    tax_id = models.CharField(max_length=50, blank=True)
    price_list = models.ForeignKey(PriceList, on_delete=models.SET_NULL, null=True, blank=True)
    payment_terms = models.CharField(max_length=20, choices=PAYMENT_TERMS_CHOICES, default='NET30')
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Billing Client"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.client_id:
            self.client_id = f"CLT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.client_id}: {self.name}"


class Invoice(models.Model):
    """Invoice for services."""

    STATUS_CHOICES = [
        ('DRAFT', 'Draft'), ('PENDING', 'Pending'),
        ('SENT', 'Sent'), ('PARTIAL', 'Partially Paid'),
        ('PAID', 'Paid'), ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled'), ('REFUNDED', 'Refunded'),
    ]

    invoice_number = models.CharField(max_length=50, unique=True, editable=False)
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='invoices')
    price_list = models.ForeignKey(PriceList, on_delete=models.PROTECT)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')

    # Dates
    invoice_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    sent_date = models.DateField(null=True, blank=True)

    # Amounts
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Billing info snapshot
    billing_address = models.TextField(blank=True)

    notes = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Invoice"
        ordering = ['-invoice_date']

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            year_month = timezone.now().strftime('%Y%m')
            count = Invoice.objects.filter(invoice_number__startswith=f"INV-{year_month}").count() + 1
            self.invoice_number = f"INV-{year_month}-{count:04d}"
        self.calculate_totals()
        super().save(*args, **kwargs)

    def calculate_totals(self):
        self.subtotal = sum(item.line_total for item in self.items.all())
        self.tax_amount = (self.subtotal - self.discount_amount) * (self.tax_rate / 100)
        self.total_amount = self.subtotal - self.discount_amount + self.tax_amount
        self.balance_due = self.total_amount - self.paid_amount

    def __str__(self):
        return f"{self.invoice_number} - {self.client.name}"


class InvoiceItem(models.Model):
    """Line item on an invoice."""

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    service_price = models.ForeignKey(ServicePrice, on_delete=models.PROTECT, null=True, blank=True)

    # Can link to specific sample/order
    molecular_sample = models.ForeignKey(
        'molecular_diagnostics.MolecularSample', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='invoice_items'
    )

    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Invoice Item"

    def save(self, *args, **kwargs):
        discount = self.quantity * self.unit_price * (self.discount_percent / 100)
        self.line_total = (self.quantity * self.unit_price) - discount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice.invoice_number}: {self.description}"


class Payment(models.Model):
    """Payment received for an invoice."""

    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'), ('CHECK', 'Check'),
        ('CARD', 'Credit/Debit Card'), ('TRANSFER', 'Bank Transfer'),
        ('ONLINE', 'Online Payment'), ('OTHER', 'Other'),
    ]

    payment_id = models.CharField(max_length=50, unique=True, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_date = models.DateField(default=timezone.now)

    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Payment"
        ordering = ['-payment_date']

    def save(self, *args, **kwargs):
        if not self.payment_id:
            self.payment_id = f"PAY-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
        # Update invoice paid amount
        self.invoice.paid_amount = sum(p.amount for p in self.invoice.payments.all())
        self.invoice.balance_due = self.invoice.total_amount - self.invoice.paid_amount
        if self.invoice.balance_due <= 0:
            self.invoice.status = 'PAID'
        elif self.invoice.paid_amount > 0:
            self.invoice.status = 'PARTIAL'
        self.invoice.save()

    def __str__(self):
        return f"{self.payment_id}: {self.amount}"


class QuotationRequest(models.Model):
    """Quotation/estimate request."""

    STATUS_CHOICES = [
        ('DRAFT', 'Draft'), ('SENT', 'Sent'),
        ('ACCEPTED', 'Accepted'), ('REJECTED', 'Rejected'),
        ('EXPIRED', 'Expired'),
    ]

    quote_number = models.CharField(max_length=50, unique=True, editable=False)
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='quotes')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')

    quote_date = models.DateField(default=timezone.now)
    valid_until = models.DateField()

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    terms_and_conditions = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    # Converted to invoice
    converted_to_invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Quotation"
        ordering = ['-quote_date']

    def save(self, *args, **kwargs):
        if not self.quote_number:
            year_month = timezone.now().strftime('%Y%m')
            count = QuotationRequest.objects.filter(quote_number__startswith=f"QUO-{year_month}").count() + 1
            self.quote_number = f"QUO-{year_month}-{count:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quote_number} - {self.client.name}"
