from decimal import Decimal
from django.db.models import F
from .models import Account   # expenses/models.py


def get_account(account_type):
    account, _ = Account.objects.get_or_create(
        account_type=account_type,
        defaults={'balance': Decimal('0')}
    )
    return account


# ====================== EXPENSE ======================
def apply_expense(amount, payment_source, amount_cash=0, amount_bank=0):
    if payment_source == 'combined':
        cash = get_account('cash')
        bank = get_account('bank')
        cash.balance = F('balance') - Decimal(amount_cash)
        bank.balance = F('balance') - Decimal(amount_bank)
        cash.save(update_fields=['balance'])
        bank.save(update_fields=['balance'])
    else:
        account = get_account(payment_source)
        account.balance = F('balance') - Decimal(amount)
        account.save(update_fields=['balance'])


def rollback_expense(amount, payment_source, amount_cash=0, amount_bank=0):
    if payment_source == 'combined':
        cash = get_account('cash')
        bank = get_account('bank')
        cash.balance = F('balance') + Decimal(amount_cash)
        bank.balance = F('balance') + Decimal(amount_bank)
        cash.save(update_fields=['balance'])
        bank.save(update_fields=['balance'])
    else:
        account = get_account(payment_source)
        account.balance = F('balance') + Decimal(amount)
        account.save(update_fields=['balance'])


# ====================== INCOME ======================
def apply_income(amount, payment_source, amount_cash=0, amount_bank=0):
    if payment_source == 'combined':
        cash = get_account('cash')
        bank = get_account('bank')
        cash.balance = F('balance') + Decimal(amount_cash)
        bank.balance = F('balance') + Decimal(amount_bank)
        cash.save(update_fields=['balance'])
        bank.save(update_fields=['balance'])
    else:
        account = get_account(payment_source)
        account.balance = F('balance') + Decimal(amount)
        account.save(update_fields=['balance'])


def rollback_income(amount, payment_source, amount_cash=0, amount_bank=0):
    if payment_source == 'combined':
        cash = get_account('cash')
        bank = get_account('bank')
        cash.balance = F('balance') - Decimal(amount_cash)
        bank.balance = F('balance') - Decimal(amount_bank)
        cash.save(update_fields=['balance'])
        bank.save(update_fields=['balance'])
    else:
        account = get_account(payment_source)
        account.balance = F('balance') - Decimal(amount)
        account.save(update_fields=['balance'])