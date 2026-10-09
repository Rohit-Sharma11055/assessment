from decimal import Decimal

from django.contrib.auth.models import Group
from django.db.models import Sum, Count
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from customers.models import Customer
from loans.models import Loan
from repayments.models import PaymentReceipt
from reconciliation.models import CashSubmission
from treasury.models import BankDeposit, BankSettlement


class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        is_admin = (
            user.is_superuser
            or user.groups.filter(
                name__in=["Administrator", "Finance/Treasury"]
            ).exists()
        )
        is_manager = user.groups.filter(name="Branch Manager").exists()
        is_agent = user.groups.filter(name="Collection Agent").exists()

        if is_admin:
            customers = Customer.objects.all()
            loans = Loan.objects.all()
            receipts = PaymentReceipt.objects.all()
            submissions = CashSubmission.objects.all()
            deposits = BankDeposit.objects.all()

        elif is_manager:
            branch_id = user.branch_manager_profile.branch_id
            customers = Customer.objects.filter(
                assignments__agent__agent_profile__home_branch_id=branch_id
            ).distinct()
            loans = Loan.objects.filter(
                customer__assignments__agent__agent_profile__home_branch_id=branch_id
            ).distinct()
            receipts = PaymentReceipt.objects.filter(
                submission_links__submission__branch_id=branch_id
            ).distinct()
            submissions = CashSubmission.objects.filter(branch_id=branch_id)
            deposits = BankDeposit.objects.filter(branch_id=branch_id)

        elif is_agent:
            customers = Customer.objects.filter(
                assignments__agent=user,
                assignments__is_active=True,
            ).distinct()
            loans = Loan.objects.filter(
                customer__assignments__agent=user,
                customer__assignments__is_active=True,
            ).distinct()
            receipts = PaymentReceipt.objects.filter(collected_by=user)
            submissions = CashSubmission.objects.filter(agent=user)
            deposits = BankDeposit.objects.none()

        else:
            return Response(
                {"error": "You do not have permission to view dashboard metrics."},
                status=403,
            )

        collected = receipts.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        pending_submissions = submissions.filter(status="PENDING").count()
        pending_deposits = deposits.exclude(
            status__in=["SETTLED", "SETTLED_WITH_DISCREPANCY", "FAILED"]
        ).count()

        settled_credits = BankSettlement.objects.filter(
            deposit__in=deposits
        ).aggregate(total=Sum("credited_amount"))["total"] or Decimal("0.00")

        return Response({
            "total_customers": customers.count(),
            "active_loans": loans.filter(status="ACTIVE").count(),
            "total_loans": loans.count(),
            "total_collected": str(collected),
            "pending_reconciliations": pending_submissions,
            "pending_deposits": pending_deposits,
            "bank_settlement_credits": str(settled_credits),
            "receipt_count": receipts.count(),
        })
