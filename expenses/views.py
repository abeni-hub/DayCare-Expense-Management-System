from rest_framework import viewsets
from .models import Account, Expense , ExpenseItem
from .serializers import AccountSerializer, ExpenseSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.decorators import action
from django.db import transaction
from .services import apply_expense, rollback_expense
from decimal import Decimal




class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    filterset_fields = ['account_type']
    search_fields = ['name']


from rest_framework import viewsets
from django.db import transaction
from decimal import Decimal

from .models import Expense
from .serializers import ExpenseSerializer
from .services import apply_expense, rollback_expense


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all().order_by('-date')
    serializer_class = ExpenseSerializer

    filterset_fields = ['category', 'payment_source', 'date']
    search_fields = ['description', 'supplier', 'category']
    ordering_fields = ['date', 'total_expense']

    @transaction.atomic
    def perform_update(self, serializer):
        # 1️⃣ Capture OLD expense values
        old_expense = self.get_object()
        old_total = old_expense.total_expense
        old_payment = old_expense.payment_source

        # 2️⃣ Rollback OLD balance
        rollback_expense(old_total, old_payment)

        # 3️⃣ Save updated expense
        # (PUT or PATCH — serializer handles items & totals)
        expense = serializer.save()

        # 4️⃣ Apply NEW balance
        apply_expense(expense.total_expense, expense.payment_source)

    @transaction.atomic
    def perform_destroy(self, instance):
        # 🔁 Rollback balance
        rollback_expense(instance.total_expense, instance.payment_source)

        # 🗑️ Delete expense
        instance.delete()
