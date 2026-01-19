# incomes/serializers.py
from rest_framework import serializers
from incomes.models import Income

class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = '__all__'
