from django.db import models

# -----------------------
# ACCOUNTS
# -----------------------
class Account(models.Model):
    ACCOUNT_TYPE = (
        ('cash', 'Cash'),
        ('bank', 'Bank'),
    )

    name = models.CharField(max_length=50)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE)
    balance = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.account_type})"


# -----------------------
# EXPENSE
# -----------------------
class Expense(models.Model):
    PAYMENT_SOURCE = (
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('both', 'Both'),
    )

    date = models.DateField()
    description = models.TextField()
    category = models.CharField(max_length=100)
    supplier = models.CharField(max_length=200, blank=True, null=True)

    payment_source = models.CharField(max_length=10, choices=PAYMENT_SOURCE)
    cash_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bank_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    total_expense = models.DecimalField(max_digits=12, decimal_places=2)

    invoice = models.FileField(upload_to='invoices/', blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Expense {self.id} - {self.total_expense}"


# -----------------------
# EXPENSE ITEMS (MULTIPLE)
# -----------------------
class ExpenseItem(models.Model):
    expense = models.ForeignKey(
        Expense,
        related_name='items',
        on_delete=models.CASCADE
    )
    item_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=50)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.item_name
