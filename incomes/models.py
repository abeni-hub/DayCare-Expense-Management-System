from django.db import models
from decimal import Decimal

class Income(models.Model):
    CATEGORY_CHOICES = (
        ('salary', 'Salary'),
        ('sales', 'Sales'),
        ('investment', 'Investment'),
        ('other', 'Other'),
    )

    date = models.DateField(db_index=True)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    payment_source = models.CharField(
        max_length=10,
        choices=[
            ('cash', 'Cash'),
            ('bank', 'Bank'),
            ('combined', 'Both / Combined')
        ],
        db_index=True
    )

    # NEW FIELDS FOR COMBINED PAYMENT
    amount_cash = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_bank = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} - {self.amount}"

    class Meta:
        ordering = ['-date']