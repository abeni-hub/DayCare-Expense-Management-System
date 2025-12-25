from rest_framework import serializers
from .models import Account, Expense, ExpenseItem


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

    def create(self, validated_data):
        items_data = validated_data.pop('items')

        expense = Expense.objects.create(**validated_data)

        total = 0
        for item in items_data:
            ExpenseItem.objects.create(expense=expense, **item)
            total += item['total']

        expense.total_expense = total
        expense.save()

        return expense


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'
