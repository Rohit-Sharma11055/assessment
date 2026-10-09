from django.conf import settings
from django.db import models
from branches.models import Branch


class BankDeposit(models.Model):
    class Status(models.TextChoices):
        PENDING_SETTLEMENT = (
            "PENDING_SETTLEMENT",
            "Pending Settlement",
        )
        SETTLED = "SETTLED", "Settled"
        SETTLED_WITH_DISCREPANCY = (
            "SETTLED_WITH_DISCREPANCY",
            "Settled with Discrepancy",
        )
        FAILED = "FAILED", "Failed"

    deposit_reference = models.CharField(
        max_length=40,
        unique=True,
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name="bank_deposits",
    )
    bank_name = models.CharField(max_length=100)
    bank_account_reference = models.CharField(max_length=50)
    deposited_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    deposit_date = models.DateField()
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING_SETTLEMENT,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_bank_deposits",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.deposit_reference


class BankSettlement(models.Model):
    deposit = models.ForeignKey(
        BankDeposit,
        on_delete=models.PROTECT,
        related_name="settlements",
    )
    bank_reference_number = models.CharField(
        max_length=100,
        unique=True,
    )
    credited_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    settlement_date = models.DateField()
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="recorded_bank_settlements",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.bank_reference_number} - "
            f"₹{self.credited_amount}"
        )


class VaultMovement(models.Model):
    class MovementType(models.TextChoices):
        CASH_RECEIVED = "CASH_RECEIVED", "Cash Received"
        BANK_DEPOSIT = "BANK_DEPOSIT", "Bank Deposit"
        ADJUSTMENT_IN = "ADJUSTMENT_IN", "Adjustment In"
        ADJUSTMENT_OUT = "ADJUSTMENT_OUT", "Adjustment Out"

    branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name="vault_movements",
    )
    movement_type = models.CharField(
        max_length=20,
        choices=MovementType.choices,
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    submission = models.ForeignKey(
        "reconciliation.CashSubmission",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="vault_movements",
    )
    deposit = models.ForeignKey(
        BankDeposit,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="vault_movements",
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="recorded_vault_movements",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"{self.branch.code} - {self.movement_type} - ₹{self.amount}"
