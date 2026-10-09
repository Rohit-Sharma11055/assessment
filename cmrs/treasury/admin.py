from django.contrib import admin
from .models import BankDeposit
from .models import BankDeposit, BankSettlement
from .models import BankDeposit, BankSettlement, VaultMovement

@admin.register(BankDeposit)
class BankDepositAdmin(admin.ModelAdmin):
    list_display = (
        "deposit_reference",
        "branch",
        "bank_name",
        "deposited_amount",
        "deposit_date",
        "status",
    )
    list_filter = ("status", "branch", "deposit_date")
    search_fields = (
        "deposit_reference",
        "bank_name",
        "branch__code",
    )
    readonly_fields = ("created_at",)


@admin.register(BankSettlement)
class BankSettlementAdmin(admin.ModelAdmin):
    list_display = (
        "bank_reference_number",
        "deposit",
        "credited_amount",
        "settlement_date",
        "recorded_by",
    )
    search_fields = (
        "bank_reference_number",
        "deposit__deposit_reference",
    )
    list_filter = ("settlement_date",)
    readonly_fields = ("created_at",)


@admin.register(VaultMovement)
class VaultMovementAdmin(admin.ModelAdmin):
    list_display = (
        "branch",
        "movement_type",
        "amount",
        "submission",
        "deposit",
        "recorded_by",
        "created_at",
    )
    list_filter = ("branch", "movement_type", "created_at")
    search_fields = (
        "branch__code",
        "deposit__deposit_reference",
        "submission__submission_reference",
    )
    readonly_fields = ("created_at",)
