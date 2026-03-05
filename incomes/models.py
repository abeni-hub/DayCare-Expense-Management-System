from django.db import models
from decimal import Decimal


class Income(models.Model):

    # ----------------------------
    # TRANSACTION TYPE
    # ----------------------------
    TRANSACTION_TYPE = [
        ('income', 'Income'),
        ('receivable', 'Receivable'),
        ('liability', 'Liability'),
    ]

    # ----------------------------
    # INCOME CATEGORY
    # ----------------------------
    CATEGORY_CHOICES = [
        ('tuition_fee', 'Child Tuition Fee'),
        ('registration_fee', 'Registration Fee'),
        ('late_fee', 'Late Payment Fee'),
        ('meal_fee', 'Meal Fee'),
        ('activity_fee', 'Activity Fee'),
        ('donation', 'Donation'),
        ('sales', 'Sales'),
        ('investment', 'Investment'),
        ('other', 'Other Income'),
    ]

    # ----------------------------
    # PAYMENT SOURCE
    # ----------------------------
    PAYMENT_SOURCE = [
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('combined', 'Combined'),
    ]

    # ----------------------------
    # PAYMENT STATUS
    # ----------------------------
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    # ----------------------------
    # BASIC INFO
    # ----------------------------
    reference_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPE,
        default='income',
        db_index=True
    )

    date = models.DateField(db_index=True)

    due_date = models.DateField(
        blank=True,
        null=True,
        help_text="Important for receivable or liability"
    )

    description = models.TextField()

    payer_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Parent name or organization"
    )

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        db_index=True
    )

    # ----------------------------
    # AMOUNT
    # ----------------------------
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    payment_source = models.CharField(
        max_length=10,
        choices=PAYMENT_SOURCE,
        db_index=True
    )

    # For combined payments
    amount_cash = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    amount_bank = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    # ----------------------------
    # RECEIVABLE / LIABILITY TRACKING
    # ----------------------------
    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    balance_due = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )

    # ----------------------------
    # EXTRA INFO
    # ----------------------------
    remarks = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    # ----------------------------
    # SAVE LOGIC
    # ----------------------------
    def save(self, *args, **kwargs):

        # Auto calculate balance
        if self.amount and self.amount_paid is not None:
            self.balance_due = self.amount - self.amount_paid

        # Auto status
        if self.balance_due == 0:
            self.status = 'paid'
        elif self.amount_paid > 0:
            self.status = 'partial'
        else:
            self.status = 'pending'

        super().save(*args, **kwargs)

    # ----------------------------
    # STRING
    # ----------------------------
    def __str__(self):
        return f"{self.transaction_type.upper()} | {self.description} | {self.amount}"

    # ----------------------------
    # ORDERING
    # ----------------------------
    class Meta:
        ordering = ['-date']