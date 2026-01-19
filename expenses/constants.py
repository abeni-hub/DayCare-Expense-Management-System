from django.db import models

class IncomeType(models.TextChoices):
    MONTHLY_FEE = 'MONTHLY_FEE', 'Monthly Parent Fee'
    REGISTRATION = 'REGISTRATION', 'Registration Fee'
    DONATION = 'DONATION', 'Donation'
    OTHER = 'OTHER', 'Other Income'