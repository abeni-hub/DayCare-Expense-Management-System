from rest_framework import serializers
from .models import Account, Expense, ExpenseItem
from django.db import transaction

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

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')

        # 1️⃣ Calculate items total
        items_total = sum(item['total'] for item in items_data)

        # 2️⃣ VAT calculation
        vat_enabled = validated_data.get('vat_enabled', False)
        vat_rate = validated_data.get('vat_rate', 15)

        vat_amount = 0
        if vat_enabled:
            vat_amount = (items_total * vat_rate) / 100

        # 3️⃣ Final total
        final_total = items_total + vat_amount

        validated_data['vat_amount'] = vat_amount
        validated_data['total_expense'] = final_total

        expense = Expense.objects.create(**validated_data)

        # 4️⃣ Save items
        for item in items_data:
            ExpenseItem.objects.create(expense=expense, **item)

        # 5️⃣ Update account balances
        if expense.payment_source == 'cash':
            cash = Account.objects.get(account_type='cash')
            cash.balance -= final_total
            cash.save()

        elif expense.payment_source == 'bank':
            bank = Account.objects.get(account_type='bank')
            bank.balance -= final_total
            bank.save()

        elif expense.payment_source == 'both':
            cash = Account.objects.get(account_type='cash')
            bank = Account.objects.get(account_type='bank')

            cash.balance -= expense.cash_amount
            bank.balance -= expense.bank_amount

            cash.save()
            bank.save()

        return expense


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'
