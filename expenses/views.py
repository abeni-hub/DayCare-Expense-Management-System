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
        """
        Interacts with FormData to parse the 'items' string into
        a list of objects before validation occurs.
        """
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            # When using FormData, request.data is an immutable QueryDict
            data = kwargs.get('data')

            if data and 'items' in data and isinstance(data['items'], str):
                mutable_data = data.copy()
                try:
                    # Convert JSON string "[{...}]" back to Python list
                    mutable_data['items'] = json.loads(data['items'])
                    kwargs['data'] = mutable_data
                except json.JSONDecodeError:
                    raise ValidationError({"items": "Invalid JSON format."})

        return super().get_serializer(*args, **kwargs)

    @transaction.atomic
    def perform_create(self, serializer):
        expense = serializer.save()
        account = get_account(expense.payment_source)

        # IMPORTANT: This is why your submission is failing right now
        # Your Cash balance is -30.00. You cannot spend more until you add Income.
        if account.balance < expense.total_expense:
            raise ValidationError(
                {"detail": f"Insufficient balance. Current: {account.balance} ETB"}
            )

        apply_expense(expense.total_expense, expense.payment_source)
    # CREATE
    # -------------------------
    @transaction.atomic
    def perform_create(self, serializer):
        # Save the expense (serializer handles item creation and total calculation)
        expense = serializer.save()

        account = get_account(expense.payment_source)

        # Validate sufficient balance
        if account.balance < expense.total_expense:
            raise ValidationError(
                {"detail": "Insufficient balance in selected account."}
            )

        # Deduct from account
        apply_expense(expense.total_expense, expense.payment_source)

    # -------------------------
    # UPDATE
    # -------------------------
    @transaction.atomic
    def perform_update(self, serializer):
        old_expense = self.get_object()

        # 1. Rollback the old deduction first to restore balance
        rollback_expense(
            old_expense.total_expense,
            old_expense.payment_source,
        )

        # 2. Save the new expense data
        expense = serializer.save()

        # 3. Re-verify balance with the new total
        account = get_account(expense.payment_source)

        if account.balance < expense.total_expense:
            # If they don't have enough, the transaction will roll back
            raise ValidationError(
                {"detail": "Insufficient balance in selected account after update."}
            )

        # 4. Apply the new deduction
        apply_expense(
            expense.total_expense,
            expense.payment_source,
        )

    # -------------------------
    # DELETE
    # -------------------------
    @transaction.atomic
    def perform_destroy(self, instance):
        # Restore money to account before deleting
        rollback_expense(
            instance.total_expense,
            instance.payment_source,
        )
        instance.delete()