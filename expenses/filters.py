from django_filters.rest_framework import FilterSet, DateFilter
from .models import Expense

class ExpenseFilter(FilterSet):
    date__gte = DateFilter(field_name='date', lookup_expr='gte')
    date__lte = DateFilter(field_name='date', lookup_expr='lte')

    class Meta:
        model = Expense
        fields = {
            'category': ['exact'],
            'payment_source': ['exact'],
            'date': ['exact'],   # keep exact too
        }