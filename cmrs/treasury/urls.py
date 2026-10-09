from django.urls import path
from .views import BankDepositListCreateView, BankSettlementCreateView

urlpatterns = [
    path("", BankDepositListCreateView.as_view(), name="bank-deposits"),
    path(
        "<int:deposit_id>/settlements/",
        BankSettlementCreateView.as_view(),
        name="bank-settlement-create",
    ),
]