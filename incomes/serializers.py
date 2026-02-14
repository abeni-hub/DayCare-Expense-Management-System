from rest_framework import serializers
from incomes.models import Income

class IncomeSerializer(serializers.ModelSerializer):
    payment_destination_name = serializers.ReadOnlyField(
        source='payment_destination.name'
    )

    income_type_display = serializers.CharField(
        source='get_income_type_display',
        read_only=True
    )

    class Meta:
        model = Income
        fields = '__all__'

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value
