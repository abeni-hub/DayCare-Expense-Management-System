from rest_framework import serializers
from .models import Income

class IncomeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Income
        fields = "__all__"
        read_only_fields = ("created_at",)

    def validate(self, data):

        payment_source = data.get("payment_source")
        amount = data.get("amount", 0)
        cash = data.get("amount_cash", 0)
        bank = data.get("amount_bank", 0)

        if payment_source == "combined":
            if cash + bank != amount:
                raise serializers.ValidationError(
                    "Cash + Bank must equal total amount."
                )

        return data