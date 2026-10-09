from django.urls import path
from .views import (
    CashSubmissionListCreateView,
    CashSubmissionVerifyView,
)

urlpatterns = [
    path("", CashSubmissionListCreateView.as_view(), name="cash-submissions"),
    path("<int:pk>/verify/", CashSubmissionVerifyView.as_view(), name="verify-cash-submission"),
]