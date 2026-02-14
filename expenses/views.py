from rest_framework import viewsets
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Account, Expense
from .serializers import AccountSerializer, ExpenseSerializer
from .services import apply_expense, rollback_expense


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['account_type']
    search_fields = ['account_type']


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.prefetch_related('items').all()
    serializer_class = ExpenseSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'payment_source', 'date']
    search_fields = ['description', 'supplier', 'category']
    ordering_fields = ['date', 'total_expense']

    @transaction.atomic
    def perform_create(self, serializer):
        expense = serializer.save()
        apply_expense(expense.total_expense, expense.payment_source)

    @transaction.atomic
    def perform_update(self, serializer):
        old_expense = self.get_object()

        rollback_expense(
            old_expense.total_expense,
            old_expense.payment_source
        )

        expense = serializer.save()

        apply_expense(
            expense.total_expense,
            expense.payment_source
        )

    @transaction.atomic
    def perform_destroy(self, instance):
        rollback_expense(
            instance.total_expense,
            instance.payment_source
        )
        instance.delete()
