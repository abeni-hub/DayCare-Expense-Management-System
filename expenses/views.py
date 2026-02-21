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

    # 🔥 FIX: Properly convert items JSON from FormData
    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        if 'items' in data and isinstance(data['items'], str):
            data['items'] = json.loads(data['items'])

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        if 'items' in data and isinstance(data['items'], str):
            data['items'] = json.loads(data['items'])

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)
        return Response(serializer.data)

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