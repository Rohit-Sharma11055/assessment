from django.contrib import admin
from .models import Loan
from .models import Loan, RepaymentSchedule


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = (
        "loan_number",
        "customer",
        "principal_amount",
        "annual_interest_rate",
        "repayment_frequency",
        "status",
        "disbursement_date",
    )
    search_fields = (
        "loan_number",
        "customer__customer_number",
        "customer__full_name",
    )
    list_filter = ("status", "repayment_frequency")



@admin.register(RepaymentSchedule)
class RepaymentScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "loan",
        "installment_number",
        "due_date",
        "principal_due",
        "interest_due",
        "principal_paid",
        "interest_paid",
        "status",
    )
    list_filter = ("status", "due_date")
    search_fields = ("loan__loan_number",)
