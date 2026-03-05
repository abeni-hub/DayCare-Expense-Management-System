from rest_framework import serializers
from decimal import Decimal
from .models import Income


class IncomeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Income
        fields = '__all__'
        read_only_fields = (
            'balance_due',
            'status',
            'created_at',
            'updated_at'
        )

    # ----------------------------
    # VALIDATIONS
    # ----------------------------
    def validate(self, data):

        payment_source = data.get('payment_source')
        amount = data.get('amount')
        amount_paid = data.get('amount_paid', Decimal('0'))

        amount_cash = data.get('amount_cash', Decimal('0'))
        amount_bank = data.get('amount_bank', Decimal('0'))

        # ----------------------------
        # Check amount_paid <= amount
        # ----------------------------
        if amount_paid and amount_paid > amount:
            raise serializers.ValidationError(
                "Amount paid cannot be greater than total amount."
            )

        # ----------------------------
        # Combined Payment Validation
        # ----------------------------
        if payment_source == "combined":

            if (amount_cash + amount_bank) != amount_paid:
                raise serializers.ValidationError(
                    "For combined payments, amount_cash + amount_bank must equal amount_paid."
                )

        # ----------------------------
        # Cash Payment Validation
        # ----------------------------
        if payment_source == "cash":
            data['amount_cash'] = amount_paid
            data['amount_bank'] = Decimal('0')

        # ----------------------------
        # Bank Payment Validation
        # ----------------------------
        if payment_source == "bank":
            data['amount_bank'] = amount_paid
            data['amount_cash'] = Decimal('0')

        return data

    # ----------------------------
    # CREATE
    # ----------------------------
    def create(self, validated_data):
        return Income.objects.create(**validated_data)

    # ----------------------------
    # UPDATE
    # ----------------------------
    def update(self, instance, validated_data):

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance