from rest_framework import serializers
from .models import Account, Expense, ExpenseItem
from django.db import transaction
from decimal import Decimal

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'

class ExpenseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseItem
        fields = '__all__'
        read_only_fields = ('expense',)


class ExpenseSerializer(serializers.ModelSerializer):
    items = ExpenseItemSerializer(many=True)

    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ('total_expense', 'vat_amount', 'created_at')

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')

        vat_enabled = validated_data.get('vat_enabled', False)
        vat_rate = validated_data.get('vat_rate', Decimal('0'))

        # 1️⃣ Create Expense first
        expense = Expense.objects.create(**validated_data)

        subtotal = Decimal('0')

        # 2️⃣ Create items & subtotal
        for item in items_data:
            total = item['quantity'] * item['unit_price']
            item['total'] = total
            subtotal += total
            ExpenseItem.objects.create(expense=expense, **item)

        # 3️⃣ VAT calculation
        vat_amount = Decimal('0')
        if vat_enabled and vat_rate > 0:
            vat_amount = (subtotal * vat_rate) / Decimal('100')

        total_expense = subtotal + vat_amount

        # 4️⃣ Save totals
        expense.vat_amount = vat_amount
        expense.total_expense = total_expense
        expense.save()

        # 5️⃣ SAFE account handling (NO DoesNotExist)
        payment_source = expense.payment_source

        if payment_source == 'cash':
            cash_account, _ = Account.objects.get_or_create(
                account_type='cash',
                defaults={'balance': Decimal('0')}
            )
            cash_account.balance -= total_expense
            cash_account.save()

        elif payment_source == 'bank':
            bank_account, _ = Account.objects.get_or_create(
                account_type='bank',
                defaults={'balance': Decimal('0')}
            )
            bank_account.balance -= total_expense
            bank_account.save()

        return expense