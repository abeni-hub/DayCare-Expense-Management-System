from rest_framework import serializers
from decimal import Decimal
from django.db import transaction

from .models import Account, Expense, ExpenseItem


class AccountSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ['id', 'account_type', 'name', 'balance']

    def get_name(self, obj):
        return obj.get_account_type_display()


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
    payment_source_display = serializers.CharField(
        source='get_payment_source_display',
        read_only=True
    )

    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = (
            'total_expense',
            'vat_amount',
            'created_at',
        )

    def validate(self, data):
        if data.get("vat_enabled") and data.get("vat_rate", 0) <= 0:
            raise serializers.ValidationError(
                "VAT rate must be greater than 0 if VAT is enabled."
            )
        return data

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        expense = Expense.objects.create(**validated_data)

        subtotal = Decimal('0')

        for item_data in items_data:
            item = ExpenseItem.objects.create(
                expense=expense,
                **item_data
            )
            subtotal += item.total

        vat_amount = Decimal('0')
        if expense.vat_enabled:
            vat_amount = subtotal * expense.vat_rate / Decimal('100')

        expense.vat_amount = vat_amount
        expense.total_expense = subtotal + vat_amount
        expense.save()

        return expense

    @transaction.atomic
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        subtotal = Decimal('0')

        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                item = ExpenseItem.objects.create(
                    expense=instance,
                    **item_data
                )
                subtotal += item.total
        else:
            for item in instance.items.all():
                subtotal += item.total

        vat_amount = Decimal('0')
        if instance.vat_enabled:
            vat_amount = subtotal * instance.vat_rate / Decimal('100')

        instance.vat_amount = vat_amount
        instance.total_expense = subtotal + vat_amount
        instance.save()

        return instance
