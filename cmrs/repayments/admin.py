from django.contrib import admin
from .models import PaymentReceipt
from .models import RepaymentAllocation


@admin.register(PaymentReceipt)
class PaymentReceiptAdmin(admin.ModelAdmin):
    list_display = (
        "receipt_number",
        "loan",
        "collected_by",
        "amount",
        "collected_at",
        "status",
    )
    search_fields = (
        "receipt_number",
        "loan__loan_number",
        "collected_by__username",
    )
    list_filter = ("status", "collected_at")
    readonly_fields = ("collected_at",)


@admin.register(RepaymentAllocation)
class RepaymentAllocationAdmin(admin.ModelAdmin):
    list_display = (
        "receipt",
        "schedule",
        "component",
        "amount",
        "created_at",
    )
    list_filter = ("component", "created_at")
    search_fields = ("receipt__receipt_number",)
    readonly_fields = ("created_at",)
