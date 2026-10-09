from django.db import models
from customers.models import Customer


class Loan(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        CLOSED = "CLOSED", "Closed"
        DEFAULTED = "DEFAULTED", "Defaulted"

    class RepaymentFrequency(models.TextChoices):
        WEEKLY = "WEEKLY", "Weekly"
        BIWEEKLY = "BIWEEKLY", "Every two weeks"
        MONTHLY = "MONTHLY", "Monthly"

    loan_number = models.CharField(
        max_length=30,
        unique=True,
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="loans",
    )
    principal_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    annual_interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )
    tenure_months = models.PositiveSmallIntegerField()
    repayment_frequency = models.CharField(
        max_length=10,
        choices=RepaymentFrequency.choices,
        default=RepaymentFrequency.MONTHLY,
    )
    disbursement_date = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.loan_number} - {self.customer.full_name}"



class RepaymentSchedule(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PARTIALLY_PAID = "PARTIALLY_PAID", "Partially Paid"
        PAID = "PAID", "Paid"
        OVERDUE = "OVERDUE", "Overdue"

    loan = models.ForeignKey(
        Loan,
        on_delete=models.PROTECT,
        related_name="repayment_schedules",
    )
    installment_number = models.PositiveSmallIntegerField()
    due_date = models.DateField()

    principal_due = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )
    interest_due = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )
    principal_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )
    interest_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    class Meta:
        ordering = ["loan", "installment_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["loan", "installment_number"],
                name="unique_installment_per_loan",
            )
        ]

    @property
    def total_due(self):
        return self.principal_due + self.interest_due

    @property
    def total_paid(self):
        return self.principal_paid + self.interest_paid

    @property
    def outstanding_amount(self):
        return self.total_due - self.total_paid

    def __str__(self):
        return f"{self.loan.loan_number} - Installment {self.installment_number}"
