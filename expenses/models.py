from django.db import models
from decimal import Decimal


class Account(models.Model):
    ACCOUNT_TYPES = (
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('combined', 'Both / Combined'),
    )

    account_type = models.CharField(
        max_length=10,
        choices=ACCOUNT_TYPES,
        unique=True,
        db_index=True
    )

    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return f"{self.account_type.upper()} - {self.balance}"


class Expense(models.Model):

    PAYMENT_SOURCE_CHOICES = (
        ('cash', 'Cash'),
        ('bank', 'Bank'),
    )

    date = models.DateField(db_index=True)
    description = models.TextField()
    category = models.CharField(max_length=100, db_index=True)
    supplier = models.CharField(max_length=255, blank=True, null=True)
    invoice = models.FileField(upload_to='invoices/%Y/%m/', blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    payment_source = models.CharField(
        max_length=10,
        choices=PAYMENT_SOURCE_CHOICES,
        db_index=True
    )

    total_expense = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - {self.total_expense}"


class ExpenseItem(models.Model):
    expense = models.ForeignKey(
        Expense,
        related_name='items',
        on_delete=models.CASCADE
    )

    item_name = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False
    )

    def save(self, *args, **kwargs):
        subtotal = self.quantity * self.unit_price
        vat = subtotal * (self.vat_rate / Decimal('100'))
        self.total = subtotal + vat
        super().save(*args, **kwargs)