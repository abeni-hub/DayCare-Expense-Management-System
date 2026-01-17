from decimal import Decimal
from .models import Account


def get_account(account_type):
    account, _ = Account.objects.get_or_create(
        account_type=account_type,
        defaults={'balance': Decimal('0')}
    )
    return account


def apply_expense(amount, payment_source):
    account = get_account(payment_source)
    account.balance -= amount
    account.save()


def rollback_expense(amount, payment_source):
    account = get_account(payment_source)
    account.balance += amount
    account.save()
