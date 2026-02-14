from django.db import models
from incomes.constants import IncomeType

class Income(models.Model):
    date = models.DateField(db_index=True)

    income_type = models.CharField(
        max_length=30,
        choices=IncomeType.choices,
        db_index=True
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
        'expenses.Account',
        on_delete=models.PROTECT,
        related_name='incomes'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.get_income_type_display()} - {self.amount}"
