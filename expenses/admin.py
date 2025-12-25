from django.contrib import admin
from .models import Account, Expense, ExpenseItem

class ExpenseItemInline(admin.TabularInline):
    model = ExpenseItem
    extra = 1

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    inlines = [ExpenseItemInline]
    list_display = ('date', 'category', 'payment_source', 'total_expense')
    list_filter = ('category', 'payment_source')

admin.site.register(Account)
