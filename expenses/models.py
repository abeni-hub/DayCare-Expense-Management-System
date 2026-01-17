from django.db import models

# -----------------------
# ACCOUNTS
# -----------------------
class Account(models.Model):
    ACCOUNT_TYPES = (
        ('cash', 'Cash'),
        ('bank', 'Bank'),
    )

    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES, unique=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

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

    date = models.DateField()
    description = models.TextField()
    category = models.CharField(max_length=100)
    supplier = models.CharField(max_length=255, blank=True, null=True)

    payment_source = models.CharField(
        max_length=10,
        choices=PAYMENT_SOURCE_CHOICES
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
        default=0,
        null=True,
        blank=True
    )

    total_expense = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,     # ✅ IMPORTANT
        blank=True     # ✅ IMPORTANT
    )

    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

# -----------------------
# EXPENSE ITEMS (MULTIPLE)
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