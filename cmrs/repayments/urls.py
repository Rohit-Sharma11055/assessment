from django.urls import path
from .views import RecordRepaymentView, ReceiptListView

urlpatterns = [
    path("", RecordRepaymentView.as_view(), name="record-repayment"),
    path("receipts/", ReceiptListView.as_view(), name="receipt-list"),
]



