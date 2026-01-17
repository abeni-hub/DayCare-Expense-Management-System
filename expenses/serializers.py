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
        fields = (
            'id',
            'item_name',
            'quantity',
            'unit',
            'unit_price',
            'total',
        )
        read_only_fields = ('total',)


class ExpenseSerializer(serializers.ModelSerializer):
    items = ExpenseItemSerializer(many=True)

    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ('total_expense', 'vat_amount', 'created_at')

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        # 🔹 Update only provided fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        subtotal = Decimal('0')

        # 🔹 Update items ONLY if provided (PATCH-safe)
        if items_data is not None:
            instance.items.all().delete()

            for item in items_data:
                total = item['quantity'] * item['unit_price']
                item['total'] = total
                subtotal += total
                ExpenseItem.objects.create(expense=instance, **item)
        else:
            # keep existing items
            for item in instance.items.all():
                subtotal += item.total

        # 🔹 VAT calculation
        vat_amount = Decimal('0')
        if instance.vat_enabled and instance.vat_rate > 0:
            vat_amount = subtotal * instance.vat_rate / Decimal('100')

        instance.vat_amount = vat_amount
        instance.total_expense = subtotal + vat_amount
        instance.save()

        return instance
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