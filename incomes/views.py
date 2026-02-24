from django.db import transaction
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError

from .models import Income
from .serializers import IncomeSerializer
from expenses.services import apply_income, rollback_income   # we'll update services.py below

class IncomeViewSet(viewsets.ModelViewSet):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'payment_source', 'date']
    search_fields = ['description', 'remarks']
    ordering_fields = ['date', 'amount']

    @transaction.atomic
    def perform_create(self, serializer):
        income = serializer.save()
        apply_income(
            income.amount,
            income.payment_source,
            income.amount_cash or 0,
            income.amount_bank or 0
        )

    @transaction.atomic
    def perform_update(self, serializer):
        old_income = self.get_object()
        rollback_income(
            old_income.amount,
            old_income.payment_source,
            old_income.amount_cash or 0,
            old_income.amount_bank or 0
        )
        income = serializer.save()
        apply_income(
            income.amount,
            income.payment_source,
            income.amount_cash or 0,
            income.amount_bank or 0
        )

    @transaction.atomic
    def perform_destroy(self, instance):
        rollback_income(
            instance.amount,
            instance.payment_source,
            instance.amount_cash or 0,
            instance.amount_bank or 0
        )
        instance.delete()