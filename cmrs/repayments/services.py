import uuid
from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.utils import timezone

from loans.models import Loan, RepaymentSchedule
from .models import PaymentReceipt, RepaymentAllocation


CENT = Decimal("0.01")


def money(value):
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


@transaction.atomic
def record_repayment(loan_id, agent, amount):
    amount = money(Decimal(str(amount)))

    if amount <= Decimal("0.00"):
        raise ValueError("Repayment amount must be positive.")

    loan = Loan.objects.select_for_update().get(pk=loan_id)

    if loan.status != Loan.Status.ACTIVE:
        raise ValueError("This loan is not active.")

    schedules = list(
        RepaymentSchedule.objects
        .select_for_update()
        .filter(loan=loan)
        .order_by("due_date", "installment_number")
    )

    if not schedules:
        raise ValueError("This loan has no repayment schedule.")

    receipt = PaymentReceipt.objects.create(
        receipt_number=f"REC-{uuid.uuid4().hex[:20].upper()}",
        loan=loan,
        collected_by=agent,
        amount=amount,
    )

    remaining = amount
    today = timezone.localdate()

    def allocate(schedule, component, available, outstanding):
        allocated = min(available, outstanding)

        if allocated <= Decimal("0.00"):
            return Decimal("0.00")

        RepaymentAllocation.objects.create(
            receipt=receipt,
            schedule=schedule,
            component=component,
            amount=allocated,
        )

        return allocated

    # First: overdue interest, then overdue principal.
    for schedule in schedules:
        if remaining <= 0 or schedule.due_date >= today:
            continue

        interest_outstanding = (
            schedule.interest_due - schedule.interest_paid
        )
        paid = allocate(
            schedule,
            RepaymentAllocation.Component.OVERDUE_INTEREST,
            remaining,
            interest_outstanding,
        )
        schedule.interest_paid += paid
        remaining -= paid

        principal_outstanding = (
            schedule.principal_due - schedule.principal_paid
        )
        paid = allocate(
            schedule,
            RepaymentAllocation.Component.PRINCIPAL,
            remaining,
            principal_outstanding,
        )
        schedule.principal_paid += paid
        remaining -= paid

    # Next: current installments, interest before principal.
    for schedule in schedules:
        if remaining <= 0 or schedule.due_date < today:
            continue

        if schedule.due_date > today:
            continue

        interest_outstanding = (
            schedule.interest_due - schedule.interest_paid
        )
        paid = allocate(
            schedule,
            RepaymentAllocation.Component.INTEREST,
            remaining,
            interest_outstanding,
        )
        schedule.interest_paid += paid
        remaining -= paid

        principal_outstanding = (
            schedule.principal_due - schedule.principal_paid
        )
        paid = allocate(
            schedule,
            RepaymentAllocation.Component.PRINCIPAL,
            remaining,
            principal_outstanding,
        )
        schedule.principal_paid += paid
        remaining -= paid

    # Future installments: pay only complete installments.
    for schedule in schedules:
        if remaining <= 0 or schedule.due_date <= today:
            continue

        interest_outstanding = (
            schedule.interest_due - schedule.interest_paid
        )
        principal_outstanding = (
            schedule.principal_due - schedule.principal_paid
        )
        installment_outstanding = (
            interest_outstanding + principal_outstanding
        )

        if remaining < installment_outstanding:
            break

        paid = allocate(
            schedule,
            RepaymentAllocation.Component.INTEREST,
            remaining,
            interest_outstanding,
        )
        schedule.interest_paid += paid
        remaining -= paid

        paid = allocate(
            schedule,
            RepaymentAllocation.Component.PRINCIPAL,
            remaining,
            principal_outstanding,
        )
        schedule.principal_paid += paid
        remaining -= paid

    # Update schedule status and save changed installments.
    for schedule in schedules:
        outstanding = (
            schedule.principal_due - schedule.principal_paid
            + schedule.interest_due - schedule.interest_paid
        )

        if outstanding == 0:
            schedule.status = RepaymentSchedule.Status.PAID
        elif schedule.due_date < today:
            schedule.status = RepaymentSchedule.Status.OVERDUE
        elif schedule.principal_paid > 0 or schedule.interest_paid > 0:
            schedule.status = RepaymentSchedule.Status.PARTIALLY_PAID
        else:
            schedule.status = RepaymentSchedule.Status.PENDING

        schedule.save(
            update_fields=[
                "principal_paid",
                "interest_paid",
                "status",
            ]
        )

    # Preserve any remainder as an unapplied advance.
    if remaining > 0:
        RepaymentAllocation.objects.create(
            receipt=receipt,
            schedule=None,
            component=RepaymentAllocation.Component.ADVANCE,
            amount=remaining,
        )

    return receipt
