import json
from rest_framework import serializers
from .models import Account, Expense, ExpenseItem
from django.db import transaction
from decimal import Decimal


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'


class ExpenseItemSerializer(serializers.ModelSerializer):
    # ✅ NEW: accept vat_rate from frontend (write-only so it doesn't appear in GET responses)
    vat_rate = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        write_only=True,
        default=Decimal('0.00')
    )

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
    items = ExpenseItemSerializer(many=True, required=False)
    cash_amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, write_only=True, required=False
    )
    bank_amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, write_only=True, required=False
    )

    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ('total_expense', 'vat_amount', 'created_at')

    # ✅ FormData JSON string handling (unchanged – already correct)
    def to_internal_value(self, data):
        data = data.copy()
        items = data.get('items')
        if items and isinstance(items, str):
            try:
                data['items'] = json.loads(items)
            except Exception:
                raise serializers.ValidationError({"items": ["Invalid JSON format."]})
        return super().to_internal_value(data)

    def _handle_account_deduction(self, expense, cash_amount, bank_amount):
        payment_source = expense.payment_source
        if payment_source == 'cash':
            cash_account, _ = Account.objects.get_or_create(
                account_type='cash', defaults={'balance': Decimal('0')}
            )
            cash_account.balance -= expense.total_expense
            cash_account.save()
        elif payment_source == 'bank':
            bank_account, _ = Account.objects.get_or_create(
                account_type='bank', defaults={'balance': Decimal('0')}
            )
            bank_account.balance -= expense.total_expense
            bank_account.save()
        elif payment_source == 'combined':
            if cash_amount > 0:
                cash_account, _ = Account.objects.get_or_create(
                    account_type='cash', defaults={'balance': Decimal('0')}
                )
                cash_account.balance -= Decimal(str(cash_amount))
                cash_account.save()
            if bank_amount > 0:
                bank_account, _ = Account.objects.get_or_create(
                    account_type='bank', defaults={'balance': Decimal('0')}
                )
                bank_account.balance -= Decimal(str(bank_amount))
                bank_account.save()
    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items', None)
        if not items_data:
            raise serializers.ValidationError({"items": ["This field is required."]})

        cash_amount = validated_data.pop('cash_amount', Decimal('0'))
        bank_amount = validated_data.pop('bank_amount', Decimal('0'))
        expense = Expense.objects.create(**validated_data)

        total_expense = Decimal('0')
        vat_amount = Decimal('0')

        for item in items_data:
            qty = Decimal(str(item['quantity']))
            unit_price = Decimal(str(item['unit_price']))
            vat_rate = Decimal(str(item.get('vat_rate', 0)))

            item_subtotal = qty * unit_price
            item_vat = item_subtotal * vat_rate / Decimal('100')
            item_total = item_subtotal + item_vat

            ExpenseItem.objects.create(
                expense=expense,
                item_name=item['item_name'],
                quantity=item['quantity'],
                unit=item.get('unit', 'pcs'),
                unit_price=item['unit_price'],
                total=item_total,
            )
            total_expense += item_total
            vat_amount += item_vat

        expense.vat_amount = vat_amount
        expense.total_expense = total_expense
        expense.save()

        self._handle_account_deduction(expense, cash_amount, bank_amount)
        return expense

    @transaction.atomic
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        cash_amount = validated_data.pop('cash_amount', Decimal('0'))
        bank_amount = validated_data.pop('bank_amount', Decimal('0'))

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            total_expense = Decimal('0')
            vat_amount = Decimal('0')
            for item in items_data:
                qty = Decimal(str(item['quantity']))
                unit_price = Decimal(str(item['unit_price']))
                vat_rate = Decimal(str(item.get('vat_rate', 0)))

                item_subtotal = qty * unit_price
                item_vat = item_subtotal * vat_rate / Decimal('100')
                item_total = item_subtotal + item_vat

                ExpenseItem.objects.create(
                    expense=instance,
                    item_name=item['item_name'],
                    quantity=item['quantity'],
                    unit=item.get('unit', 'pcs'),
                    unit_price=item['unit_price'],
                    total=item_total,
                )
                total_expense += item_total
                vat_amount += item_vat
        else:
            total_expense = Decimal('0')
            vat_amount = getattr(instance, 'vat_amount', Decimal('0'))
            for item in instance.items.all():
                total_expense += Decimal(str(item.total))

        instance.vat_amount = vat_amount
        instance.total_expense = total_expense
        instance.save()

        self._handle_account_deduction(instance, cash_amount, bank_amount)
        return instance