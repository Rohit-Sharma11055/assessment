from datetime import date
from decimal import Decimal

from django.test import TestCase

from customers.models import Customer
from loans.models import Loan, RepaymentSchedule
from loans.services import generate_repayment_schedule


class RepaymentScheduleTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            customer_number="TEST-CUS-001",
            full_name="Test Customer",
            phone="9999999999",
        )

        self.loan = Loan.objects.create(
            loan_number="TEST-LN-001",
            customer=self.customer,
            principal_amount=Decimal("50000.00"),
            annual_interest_rate=Decimal("12.00"),
            tenure_months=12,
            repayment_frequency=Loan.RepaymentFrequency.MONTHLY,
            disbursement_date=date(2026, 1, 15),
            status=Loan.Status.ACTIVE,
        )

    def test_generates_correct_number_of_installments(self):
        generate_repayment_schedule(self.loan.id)

        self.assertEqual(
            self.loan.repayment_schedules.count(),
            12,
        )

    def test_principal_and_interest_totals_are_exact(self):
        generate_repayment_schedule(self.loan.id)

        schedules = self.loan.repayment_schedules.all()

        total_principal = sum(
            (item.principal_due for item in schedules),
            Decimal("0.00"),
        )
        total_interest = sum(
            (item.interest_due for item in schedules),
            Decimal("0.00"),
        )

        self.assertEqual(total_principal, Decimal("50000.00"))
        self.assertEqual(total_interest, Decimal("6000.00"))

    def test_installment_dates_are_monthly(self):
        generate_repayment_schedule(self.loan.id)

        schedules = list(
            self.loan.repayment_schedules.order_by(
                "installment_number"
            )
        )

        self.assertEqual(schedules[0].due_date, date(2026, 2, 15))
        self.assertEqual(schedules[-1].due_date, date(2027, 1, 15))

    def test_duplicate_schedule_generation_is_rejected(self):
        generate_repayment_schedule(self.loan.id)

        with self.assertRaisesMessage(
            ValueError,
            "A schedule already exists",
        ):
            generate_repayment_schedule(self.loan.id)

        self.assertEqual(self.loan.repayment_schedules.count(), 12)

    def test_zero_tenure_is_rejected(self):
        self.loan.tenure_months = 0
        self.loan.save()

        with self.assertRaisesMessage(
            ValueError,
            "Loan tenure must be positive",
        ):
            generate_repayment_schedule(self.loan.id)

        self.assertEqual(self.loan.repayment_schedules.count(), 0)
