# finances/services.py
from decimal import Decimal

def apply_income(amount, account):
    account.balance += Decimal(amount)
    account.save(update_fields=['balance'])

def rollback_income(amount, account):
    account.balance -= Decimal(amount)
    account.save(update_fields=['balance'])
