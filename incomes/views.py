# incomes/views.py
from rest_framework import viewsets
from django.db import transaction
from incomes.models import Income
from incomes.serializers import IncomeSerializer
from finances.services import apply_income, rollback_income

class IncomeViewSet(viewsets.ModelViewSet):
    queryset = Income.objects.all().order_by('-date')
    serializer_class = IncomeSerializer

    filterset_fields = ['income_type', 'date', 'payment_destination']
    search_fields = ['parent', 'description']
    ordering_fields = ['date', 'amount']

    @transaction.atomic
    def perform_create(self, serializer):
        income = serializer.save()
        apply_income(income.amount, income.payment_destination)

    @transaction.atomic
    def perform_update(self, serializer):
        old_income = self.get_object()

        rollback_income(old_income.amount, old_income.payment_destination)

        income = serializer.save()

        apply_income(income.amount, income.payment_destination)

    @transaction.atomic
    def perform_destroy(self, instance):
        rollback_income(instance.amount, instance.payment_destination)
        instance.delete()
