from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from loans.models import Loan
from customers.models import CustomerAssignment
from accounts.permissions import (
    is_admin,
    is_collection_agent,
)
from .models import PaymentReceipt
from .serializers import RepaymentSerializer
from .services import record_repayment


class RecordRepaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        admin = is_admin(user)

        if not (admin or is_collection_agent(user)):
            return Response(
                {"error": "Collection Agent role required."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = RepaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        loan_id = serializer.validated_data["loan_id"]
        amount = serializer.validated_data["amount"]

        # Agents may collect only for currently assigned customers.
        if not admin:
            assigned = CustomerAssignment.objects.filter(
                customer__loans__id=loan_id,
                agent=user,
                is_active=True,
            ).exists()

            if not assigned:
                return Response(
                    {"error": "Loan is not assigned to you."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        try:
            receipt = record_repayment(
                loan_id=loan_id,
                agent=user,
                amount=amount,
            )
        except (ValueError, Loan.DoesNotExist) as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "receipt_number": receipt.receipt_number,
                "loan_id": receipt.loan_id,
                "amount": str(receipt.amount),
                "status": receipt.status,
                "message": "Repayment recorded successfully.",
            },
            status=status.HTTP_201_CREATED,
        )


class ReceiptListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        receipts = PaymentReceipt.objects.select_related(
            "loan", "loan__customer", "collected_by"
        ).order_by("-collected_at")

        # Administrator can inspect all receipts.
        if is_admin(user):
            pass

        # Agents can inspect only their own receipts.
        elif is_collection_agent(user):
            receipts = receipts.filter(collected_by=user)

        # All other roles are denied from this Collections endpoint.
        else:
            raise PermissionDenied(
                "Your role cannot access the Collections page."
            )

        data = [
            {
                "id": receipt.id,
                "receipt_number": receipt.receipt_number,
                "loan_id": receipt.loan_id,
                "customer_name": receipt.loan.customer.full_name,
                "amount": str(receipt.amount),
                "status": receipt.status,
                "collected_at": receipt.collected_at,
            }
            for receipt in receipts
        ]

        return Response(data)
