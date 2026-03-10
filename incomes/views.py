from django.db import transaction
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Income
from .serializers import IncomeSerializer
from expenses.services import apply_income, rollback_income

class IncomeViewSet(viewsets.ModelViewSet):
    queryset = Income.objects.all().order_by('-date')
    serializer_class = IncomeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = ['transaction_type', 'category', 'payment_source', 'status', 'date']
    search_fields = ['description', 'payer_name', 'reference_number', 'remarks']
    ordering_fields = ['date', 'amount', 'amount_paid', 'created_at']

    @transaction.atomic
    def perform_create(self, serializer):
        income = serializer.save()

        if income.amount_paid > 0:
            apply_income(
                income.amount_paid,
                income.payment_source,
                income.amount_cash or 0,
                income.amount_bank or 0
            )

    @transaction.atomic
    def perform_update(self, serializer):
        # Get the database state BEFORE the update
        old_income = self.get_object()

        # Rollback previous applied money
        if old_income.amount_paid > 0:
            rollback_income(
                old_income.amount_paid,
                old_income.payment_source,
                old_income.amount_cash or 0,
                old_income.amount_bank or 0
            )

        # Save new data
        income = serializer.save()

        # Apply new payment
        if income.amount_paid > 0:
            apply_income(
                income.amount_paid,
                income.payment_source,
                income.amount_cash or 0,
                income.amount_bank or 0
            )

    @transaction.atomic
    def perform_destroy(self, instance):
        if instance.amount_paid > 0:
            rollback_income(
                instance.amount_paid,
                instance.payment_source,
                instance.amount_cash or 0,
                instance.amount_bank or 0
            )
        instance.delete()