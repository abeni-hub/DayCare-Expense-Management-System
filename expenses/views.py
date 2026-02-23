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
from .filters import ExpenseFilter   # ← NEW IMPORT

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
    filterset_class = ExpenseFilter
    search_fields = ["description", "supplier", "category", "remarks"]
    ordering_fields = ["date", "total_expense"]

    # -------------------------
    # CREATE
    # -------------------------
    @transaction.atomic
    def perform_create(self, serializer):
        expense = serializer.save()

        if expense.payment_source == "combined":
            cash_amount = Decimal(self.request.data.get("cash_amount", 0))
            bank_amount = Decimal(self.request.data.get("bank_amount", 0))

            if cash_amount + bank_amount != expense.total_expense:
                raise ValidationError({"detail": "Cash + Bank must equal total expense."})

            cash_account = get_account("cash")
            bank_account = get_account("bank")

            if cash_account.balance < cash_amount:
                raise ValidationError({"detail": "Insufficient cash balance."})

            if bank_account.balance < bank_amount:
                raise ValidationError({"detail": "Insufficient bank balance."})

            apply_expense(cash_amount, "cash")
            apply_expense(bank_amount, "bank")

        else:
            account = get_account(expense.payment_source)

            if account.balance < expense.total_expense:
                raise ValidationError({"detail": "Insufficient balance in selected account."})

            apply_expense(expense.total_expense, expense.payment_source)

    # -------------------------
    # UPDATE
    # -------------------------
    @transaction.atomic
    def perform_update(self, serializer):
        old_expense = self.get_object()

        # Rollback OLD transaction first
        if old_expense.payment_source == "combined":
            old_cash = Decimal(self.request.data.get("cash_amount", 0))
            old_bank = Decimal(self.request.data.get("bank_amount", 0))

            rollback_expense(old_cash, "cash")
            rollback_expense(old_bank, "bank")
        else:
            rollback_expense(old_expense.total_expense, old_expense.payment_source)

        expense = serializer.save()

        if expense.payment_source == "combined":
            cash_amount = Decimal(self.request.data.get("cash_amount", 0))
            bank_amount = Decimal(self.request.data.get("bank_amount", 0))

            if cash_amount + bank_amount != expense.total_expense:
                raise ValidationError({"detail": "Cash + Bank must equal total expense."})

            cash_account = get_account("cash")
            bank_account = get_account("bank")

            if cash_account.balance < cash_amount:
                raise ValidationError({"detail": "Insufficient cash balance after update."})

            if bank_account.balance < bank_amount:
                raise ValidationError({"detail": "Insufficient bank balance after update."})

            apply_expense(cash_amount, "cash")
            apply_expense(bank_amount, "bank")

        else:
            account = get_account(expense.payment_source)

            if account.balance < expense.total_expense:
                raise ValidationError({"detail": "Insufficient balance after update."})

            apply_expense(expense.total_expense, expense.payment_source)

    # -------------------------
    # DELETE
    # -------------------------
    @transaction.atomic
    def perform_destroy(self, instance):

        if instance.payment_source == "combined":
            # We assume frontend always sends correct split again if needed
            cash_amount = Decimal(self.request.data.get("cash_amount", 0))
            bank_amount = Decimal(self.request.data.get("bank_amount", 0))

            rollback_expense(cash_amount, "cash")
            rollback_expense(bank_amount, "bank")
        else:
            rollback_expense(instance.total_expense, instance.payment_source)

        instance.delete()