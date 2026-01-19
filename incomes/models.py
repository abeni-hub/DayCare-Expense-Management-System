# incomes/models.py
from django.db import models
from incomes.constants import IncomeType

class Income(models.Model):
    date = models.DateField()

    income_type = models.CharField(
        max_length=30,
        choices=IncomeType.choices
    )

    parent = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    description = models.TextField(blank=True)

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    payment_destination = models.ForeignKey(
        'accounts.Account',
        on_delete=models.PROTECT
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.income_type} - {self.amount}"
