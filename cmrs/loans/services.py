import calendar
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction

from .models import Loan, RepaymentSchedule


CENT = Decimal("0.01")


def money(value):
    """Round a monetary value to two decimal places."""
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def add_months(start_date, months):
    """Add months while keeping dates valid at month-end."""
    month_index = start_date.month - 1 + months
    year = start_date.year + month_index // 12
    month = month_index % 12 + 1

    day = min(
        start_date.day,
        calendar.monthrange(year, month)[1],
    )

    return date(year, month, day)


@transaction.atomic
def generate_repayment_schedule(loan_id):
    loan = Loan.objects.select_for_update().get(pk=loan_id)

    if loan.status != Loan.Status.ACTIVE:
        raise ValueError("Only active loans can receive a schedule.")

    if loan.repayment_frequency != Loan.RepaymentFrequency.MONTHLY:
        raise ValueError("This version supports monthly schedules only.")

    if loan.tenure_months <= 0:
        raise ValueError("Loan tenure must be positive.")

    if loan.principal_amount <= 0:
        raise ValueError("Loan principal must be positive.")

    if loan.annual_interest_rate < 0:
        raise ValueError("Interest rate cannot be negative.")

    if RepaymentSchedule.objects.filter(loan=loan).exists():
        raise ValueError("A schedule already exists for this loan.")

    principal = loan.principal_amount
    rate = loan.annual_interest_rate / Decimal("100")
    tenure = loan.tenure_months

    total_interest = money(
        principal * rate * Decimal(tenure) / Decimal("12")
    )

    principal_per_installment = money(
        principal / Decimal(tenure)
    )
    interest_per_installment = money(
        total_interest / Decimal(tenure)
    )

    remaining_principal = principal
    remaining_interest = total_interest
    schedules = []

    for number in range(1, tenure + 1):
        if number == tenure:
            # Final installment absorbs all rounding differences.
            principal_due = remaining_principal
            interest_due = remaining_interest
        else:
            principal_due = principal_per_installment
            interest_due = interest_per_installment

        schedules.append(
            RepaymentSchedule(
                loan=loan,
                installment_number=number,
                due_date=add_months(
                    loan.disbursement_date,
                    number,
                ),
                principal_due=principal_due,
                interest_due=interest_due,
                principal_paid=Decimal("0.00"),
                interest_paid=Decimal("0.00"),
                status=RepaymentSchedule.Status.PENDING,
            )
        )

        remaining_principal -= principal_due
        remaining_interest -= interest_due

    RepaymentSchedule.objects.bulk_create(schedules)

    return schedules
