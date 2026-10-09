
from django.urls import path
from .views import LoanListView

urlpatterns = [
    path("", LoanListView.as_view(), name="loan-list"),
]
