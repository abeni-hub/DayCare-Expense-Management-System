from django.db import models
from decimal import Decimal


# -----------------------
# ACCOUNTS
# -----------------------
class Account(models.Model):
    ACCOUNT_TYPES = (
        ('cash', 'Cash'),
        ('bank', 'Bank'),
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

    class Meta:
        ordering = ['account_type']

    def __str__(self):
        return f"{self.account_type.upper()} - {self.balance}"

# -----------------------
# EXPENSE
# -----------------------
class Expense(models.Model):

    PAYMENT_SOURCE_CHOICES = (
        ('cash', 'Cash'),
        ('bank', 'Bank'),
    )

    date = models.DateField(db_index=True)
    description = models.TextField()
    category = models.CharField(max_length=100, db_index=True)
    supplier = models.CharField(max_length=255, blank=True, null=True)

    payment_source = models.CharField(
        max_length=10,
        choices=PAYMENT_SOURCE_CHOICES,
        db_index=True
    )

    vat_enabled = models.BooleanField(default=False)

    vat_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    vat_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    total_expense = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.category} - {self.total_expense}"


# -----------------------
# EXPENSE ITEMS
# -----------------------
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

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False
    )

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
