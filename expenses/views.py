import json
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Account, Expense
from .serializers import AccountSerializer, ExpenseSerializer
from .services import apply_expense, get_account, rollback_expense


# -----------------------------
# ACCOUNT VIEWSET
# -----------------------------
class AccountViewSet(ReadOnlyModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        accounts_data = serializer.data

        # Compute combined total safely
        total_balance = (
            queryset.aggregate(total=Sum("balance"))["total"]
            or Decimal("0")
        )

        combined_account = {
            "id": "combined",
            "account_type": "combined",
            "name": "Combined Total",
            "balance": total_balance,
        }

        return Response([combined_account] + accounts_data)


# -----------------------------
# EXPENSE VIEWSET
# -----------------------------
class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.prefetch_related("items").all()
    serializer_class = ExpenseSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["category", "payment_source", "date"]
    search_fields = ["description", "supplier", "category", "remarks"]
    ordering_fields = ["date", "total_expense"]

    def get_serializer(self, *args, **kwargs):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            data = kwargs.get('data')

            if data and 'items' in data and isinstance(data['items'], str):
                mutable_data = data.copy()
                mutable_data['items'] = json.loads(data['items'])
                kwargs['data'] = mutable_data

        return super().get_serializer(*args, **kwargs)

    @transaction.atomic
    def perform_create(self, serializer):
        expense = serializer.save()
        account = get_account(expense.payment_source)

        if account.balance < expense.total_expense:
            raise ValidationError(
                {"detail": "Insufficient balance in selected account."}
            )

        apply_expense(expense.total_expense, expense.payment_source)

    @transaction.atomic
    def perform_update(self, serializer):
        old_expense = self.get_object()

        rollback_expense(
            old_expense.total_expense,
            old_expense.payment_source,
        )

        expense = serializer.save()

        account = get_account(expense.payment_source)

        if account.balance < expense.total_expense:
            raise ValidationError(
                {"detail": "Insufficient balance after update."}
            )

        apply_expense(expense.total_expense, expense.payment_source)

    @transaction.atomic
    def perform_destroy(self, instance):
        rollback_expense(
            instance.total_expense,
            instance.payment_source,
        )
        instance.delete()