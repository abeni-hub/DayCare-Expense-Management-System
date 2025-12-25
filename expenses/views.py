from rest_framework import viewsets
from .models import Account, Expense
from .serializers import AccountSerializer, ExpenseSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from rest_framework.views import APIView 
from rest_framework.response import Response 
from rest_framework import filters
from rest_framework.decorators import action



class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    filterset_fields = ['account_type']
    search_fields = ['name']


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all().order_by('-date')
    serializer_class = ExpenseSerializer

    filterset_fields = ['category', 'payment_source', 'date']
    search_fields = ['description', 'supplier', 'category']
    ordering_fields = ['date', 'total_expense']

    @action(detail=False, methods=['get'])
    def daily_report(self, request):
        data = (
            Expense.objects
            .annotate(day=TruncDay('date'))
            .values('day')
            .annotate(total=Sum('total_expense'))
            .order_by('-day')
        )
        return Response(data)

    @action(detail=False, methods=['get'])
    def monthly_report(self, request):
        data = (
            Expense.objects
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(total=Sum('total_expense'))
            .order_by('-month')
        )
        return Response(data)

    @action(detail=False, methods=['get'])
    def category_report(self, request):
        data = (
            Expense.objects
            .values('category')
            .annotate(total=Sum('total_expense'))
            .order_by('-total')
        )
        return Response(data)