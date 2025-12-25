from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExpenseViewSet, AccountViewSet

router = DefaultRouter()
router.register('accounts', AccountViewSet, basename='accounts')
router.register('expenses', ExpenseViewSet, basename='expenses')

# ------------------------
# EXPLICIT REPORT URLS
# ------------------------
expense_report_list = ExpenseViewSet.as_view({
    'get': 'daily_report'
})

expense_monthly_report = ExpenseViewSet.as_view({
    'get': 'monthly_report'
})

expense_category_report = ExpenseViewSet.as_view({
    'get': 'category_report'
})

urlpatterns = [
    path('', include(router.urls)),

    # Reports (EXPLICIT)
    path(
        'expenses/reports/daily/',
        ExpenseViewSet.as_view({'get': 'daily_report'}),
        name='expense-daily-report'
    ),
    path(
        'expenses/reports/monthly/',
        ExpenseViewSet.as_view({'get': 'monthly_report'}),
        name='expense-monthly-report'
    ),
    path(
        'expenses/reports/category/',
        ExpenseViewSet.as_view({'get': 'category_report'}),
        name='expense-category-report'
    ),
]
