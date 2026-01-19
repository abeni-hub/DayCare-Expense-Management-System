# incomes/urls.py
from rest_framework.routers import DefaultRouter
from incomes.views import IncomeViewSet

router = DefaultRouter()
router.register(r'incomes', IncomeViewSet)

urlpatterns = router.urls
