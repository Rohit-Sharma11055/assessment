from django.contrib import admin
from .models import CashSubmission
from .models import SubmissionReceipt


@admin.register(CashSubmission)
class CashSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "submission_reference",
        "agent",
        "branch",
        "expected_amount",
        "actual_amount",
        "status",
        "submitted_at",
    )
    list_filter = ("status", "branch", "submitted_at")
    search_fields = (
        "submission_reference",
        "agent__username",
        "branch__code",
    )
    readonly_fields = ("submitted_at",)


@admin.register(SubmissionReceipt)
class SubmissionReceiptAdmin(admin.ModelAdmin):
    list_display = (
        "submission",
        "receipt",
        "linked_at",
    )
    search_fields = (
        "submission__submission_reference",
        "receipt__receipt_number",
    )
    readonly_fields = ("linked_at",)
