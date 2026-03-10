from rest_framework import serializers
from .models import Income

class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = "__all__"
        read_only_fields = ("created_at",)

    def validate(self, data):
        # Use existing instance data if it's a partial update (PATCH)
        payment_source = data.get("payment_source", getattr(self.instance, 'payment_source', None))
        amount_paid = data.get("amount_paid", getattr(self.instance, 'amount_paid', 0))
        cash = data.get("amount_cash", getattr(self.instance, 'amount_cash', 0))
        bank = data.get("amount_bank", getattr(self.instance, 'amount_bank', 0))

        if payment_source == "combined":
            # Compare with amount_paid instead of total amount
            if (cash + bank) != amount_paid:
                raise serializers.ValidationError({
                    "payment_source": f"Cash ({cash}) + Bank ({bank}) must equal Amount Paid ({amount_paid})."
                })

        return data