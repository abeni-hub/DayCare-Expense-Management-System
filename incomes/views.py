from rest_framework import viewsets
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from incomes.models import Income
from incomes.serializers import IncomeSerializer
from finances.services import apply_income, rollback_income


class IncomeViewSet(viewsets.ModelViewSet):
    queryset = Income.objects.select_related('payment_destination').all()
    serializer_class = IncomeSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

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

        # rollback old transaction first
        rollback_income(old_income.amount, old_income.payment_destination)

        income = serializer.save()

        # apply new transaction
        apply_income(income.amount, income.payment_destination)

    @transaction.atomic
    def perform_destroy(self, instance):
        rollback_income(instance.amount, instance.payment_destination)
        instance.delete()
