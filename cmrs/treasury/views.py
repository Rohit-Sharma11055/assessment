import uuid
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.db.models import Sum

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import is_admin, is_finance_treasury
from branches.models import Branch
from .models import BankDeposit, BankSettlement, VaultMovement
from .serializers import BankDepositSerializer


def can_manage_treasury(user):
    return is_admin(user) or is_finance_treasury(user)


def vault_balance(branch_id):
    movements = VaultMovement.objects.filter(branch_id=branch_id)

    incoming = movements.filter(
        movement_type__in=["CASH_RECEIVED", "ADJUSTMENT_IN"]
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    outgoing = movements.filter(
        movement_type__in=["BANK_DEPOSIT", "ADJUSTMENT_OUT"]
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    return incoming - outgoing


class BankDepositListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not can_manage_treasury(request.user):
            return Response(
                {"error": "Finance/Treasury role required."},
                status=status.HTTP_403_FORBIDDEN,
            )

        deposits = BankDeposit.objects.select_related(
            "branch", "created_by"
        ).prefetch_related(
            "banksettlement_set"
        ).order_by("-created_at")

        return Response(
            BankDepositSerializer(deposits, many=True).data
        )

    @transaction.atomic
    def post(self, request):
        if not can_manage_treasury(request.user):
            return Response(
                {"error": "Finance/Treasury role required."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            branch_id = int(request.data.get("branch"))
            amount = Decimal(str(request.data.get("deposited_amount")))
            deposit_date = request.data.get("deposit_date")
            bank_name = str(request.data.get("bank_name", "")).strip()
            account_ref = str(
                request.data.get("bank_account_reference", "")
            ).strip()

            if not amount.is_finite() or amount <= 0:
                raise ValueError

            if not bank_name or not account_ref or not deposit_date:
                raise ValueError

        except (TypeError, ValueError, InvalidOperation):
            return Response(
                {
                    "error": (
                        "Provide a valid branch, positive amount, date, "
                        "bank and account reference."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            branch = Branch.objects.select_for_update().get(pk=branch_id)
        except Branch.DoesNotExist:
            return Response(
                {"error": "Branch not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if amount > vault_balance(branch.pk):
            return Response(
                {"error": "Deposit exceeds available branch vault cash."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        deposit = BankDeposit.objects.create(
            deposit_reference=f"BD-{uuid.uuid4().hex[:12].upper()}",
            branch=branch,
            bank_name=bank_name,
            bank_account_reference=account_ref,
            deposited_amount=amount,
            deposit_date=deposit_date,
            created_by=request.user,
            notes=request.data.get("notes", ""),
        )

        VaultMovement.objects.create(
            branch=branch,
            movement_type="BANK_DEPOSIT",
            amount=amount,
            deposit=deposit,
            recorded_by=request.user,
            notes=f"Bank deposit {deposit.deposit_reference}",
        )

        return Response(
            BankDepositSerializer(deposit).data,
            status=status.HTTP_201_CREATED,
        )


class BankSettlementCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, deposit_id):
        if not can_manage_treasury(request.user):
            return Response(
                {"error": "Finance/Treasury role required."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            deposit = BankDeposit.objects.select_for_update().get(
                pk=deposit_id
            )
        except BankDeposit.DoesNotExist:
            return Response(
                {"error": "Deposit not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if deposit.status in [
            "SETTLED",
            "SETTLED_WITH_DISCREPANCY",
            "FAILED",
        ]:
            return Response(
                {"error": "This deposit is no longer open for settlement."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            amount = Decimal(str(request.data.get("credited_amount")))
            settlement_date = request.data.get("settlement_date")
            bank_ref = str(
                request.data.get("bank_reference_number", "")
            ).strip()

            if not amount.is_finite() or amount <= 0:
                raise ValueError

            if not bank_ref or not settlement_date:
                raise ValueError

        except (TypeError, ValueError, InvalidOperation):
            return Response(
                {
                    "error": (
                        "Provide a positive credit amount, settlement "
                        "date and bank reference."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        previous = BankSettlement.objects.filter(
            deposit=deposit
        ).aggregate(total=Sum("credited_amount"))["total"] or Decimal("0.00")

        if previous + amount > deposit.deposited_amount:
            return Response(
                {
                    "error": (
                        "Total bank credits cannot exceed "
                        "the deposit amount."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        settlement = BankSettlement.objects.create(
            deposit=deposit,
            bank_reference_number=bank_ref,
            credited_amount=amount,
            settlement_date=settlement_date,
            recorded_by=request.user,
            notes=request.data.get("notes", ""),
        )

        total = previous + amount

        deposit.status = (
            "SETTLED"
            if total == deposit.deposited_amount
            else "PENDING_SETTLEMENT"
        )
        deposit.save(update_fields=["status"])

        return Response(
            {
                "id": settlement.id,
                "deposit_reference": deposit.deposit_reference,
                "credited_amount": str(settlement.credited_amount),
                "total_credited": str(total),
                "outstanding_amount": str(
                    deposit.deposited_amount - total
                ),
                "deposit_status": deposit.status,
            },
            status=status.HTTP_201_CREATED,
        )
