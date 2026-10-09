from django.conf import settings
from django.db import models
from loans.models import Loan


class PaymentReceipt(models.Model):
    class Status(models.TextChoices):
        COLLECTED = "COLLECTED", "Collected"
        SUBMITTED = "SUBMITTED", "Submitted to Branch"
        RECONCILED = "RECONCILED", "Reconciled at Branch"

    receipt_number = models.CharField(
        max_length=40,
        unique=True,
    )
    loan = models.ForeignKey(
        Loan,
        on_delete=models.PROTECT,
        related_name="receipts",
    )
    collected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="collected_receipts",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    collected_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.COLLECTED,
    )

    class Meta:
        ordering = ["-collected_at"]

    def __str__(self):
        return f"{self.receipt_number} - ₹{self.amount}"



from loans.models import RepaymentSchedule


class RepaymentAllocation(models.Model):
    class Component(models.TextChoices):
        PENALTY = "PENALTY", "Penalty"
        OVERDUE_INTEREST = "OVERDUE_INTEREST", "Overdue Interest"
        PRINCIPAL = "PRINCIPAL", "Principal"
        INTEREST = "INTEREST", "Interest"
        ADVANCE = "ADVANCE", "Advance Payment"

    receipt = models.ForeignKey(
        PaymentReceipt,
        on_delete=models.PROTECT,
        related_name="allocations",
    )
    schedule = models.ForeignKey(
        RepaymentSchedule,
        on_delete=models.PROTECT,
        related_name="allocations",
        null=True,
        blank=True,
    )
    component = models.CharField(
        max_length=20,
        choices=Component.choices,
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.receipt.receipt_number} - "
            f"{self.component} - ₹{self.amount}"
        )
