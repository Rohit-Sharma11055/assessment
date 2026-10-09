from django.conf import settings
from django.db import models
from branches.models import Branch
from repayments.models import PaymentReceipt


class CashSubmission(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        APPROVED_WITH_DISCREPANCY = (
            "APPROVED_WITH_DISCREPANCY",
            "Approved with Discrepancy",
        )
        REJECTED = "REJECTED", "Rejected"

    submission_reference = models.CharField(
        max_length=40,
        unique=True,
    )
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="cash_submissions",
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name="cash_submissions",
    )
    expected_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    actual_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    discrepancy_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="verified_cash_submissions",
        null=True,
        blank=True,
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.submission_reference



class SubmissionReceipt(models.Model):
    submission = models.ForeignKey(
        CashSubmission,
        on_delete=models.PROTECT,
        related_name="receipt_links",
    )
    receipt = models.ForeignKey(
        PaymentReceipt,
        on_delete=models.PROTECT,
        related_name="submission_links",
    )
    linked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["submission", "receipt"],
                name="unique_receipt_per_submission",
            )
        ]

    def __str__(self):
        return (
            f"{self.submission.submission_reference} - "
            f"{self.receipt.receipt_number}"
        )
