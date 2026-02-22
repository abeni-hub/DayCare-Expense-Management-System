from rest_framework import serializers
from decimal import Decimal
import json
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
    vat_rate = serializers.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        model = ExpenseItem
        fields = (
            'id',
            'item_name',
            'quantity',
            'unit',
            'unit_price',
            'vat_rate',
            'total',
        )
        read_only_fields = ('total',)


class ExpenseSerializer(serializers.ModelSerializer):
    # ── For READING (GET list / detail) ──
    items = ExpenseItemSerializer(many=True, read_only=True)

    # ── For WRITING (POST/PUT from React FormData) ──
    items_input = serializers.JSONField(write_only=True)

    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ('total_expense', 'created_at')

    def validate_items_input(self, value):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                raise serializers.ValidationError("Invalid JSON format for items.")

        if not isinstance(value, list) or len(value) == 0:
            raise serializers.ValidationError("At least one item is required.")

        item_serializer = ExpenseItemSerializer(data=value, many=True)
        if not item_serializer.is_valid():
            raise serializers.ValidationError(item_serializer.errors)

        return item_serializer.validated_data

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items_input')
        expense = Expense.objects.create(**validated_data)

        grand_total = Decimal('0')
        for item_data in items_data:
            item = ExpenseItem.objects.create(expense=expense, **item_data)
            grand_total += item.total

        expense.total_expense = grand_total
        expense.save()
        return expense

    @transaction.atomic
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items_input', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            grand_total = Decimal('0')
            for item_data in items_data:
                item = ExpenseItem.objects.create(expense=instance, **item_data)
                grand_total += item.total
            instance.total_expense = grand_total
            instance.save()

        return instance