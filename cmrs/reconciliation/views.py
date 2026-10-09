import uuid
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import is_admin, is_collection_agent, is_branch_manager
from repayments.models import PaymentReceipt
from treasury.models import VaultMovement
from .models import CashSubmission, SubmissionReceipt
from .serializers import CashSubmissionSerializer


class CashSubmissionListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Reconciliation's receipt picker is separate from the Collections page.
        # Branch Managers can view all unsubmitted receipts to confirm a deposit.
        if request.query_params.get("type") == "receipts":
            if not (is_admin(user) or is_branch_manager(user) or is_collection_agent(user)):
                return Response(
                    {"error": "Your role cannot access reconciliation receipts."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            receipts = PaymentReceipt.objects.filter(
                status="COLLECTED"
            ).select_related(
                "loan", "loan__customer", "collected_by"
            ).order_by("-collected_at")

            # Scope managers to their own branch using the server-side profile,
            # never a branch ID supplied by the browser/token.
            if is_branch_manager(user) and not is_admin(user):
                manager_profile = getattr(user, "branch_manager_profile", None)
                manager_branch_id = getattr(manager_profile, "branch_id", None)
                if not manager_branch_id:
                    return Response(
                        {"error": "Your account has no home branch configured."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                receipts = receipts.filter(
                    collected_by__agent_profile__home_branch_id=manager_branch_id
                )

            # Agents only see receipts they personally collected.
            elif is_collection_agent(user) and not is_admin(user):
                receipts = receipts.filter(collected_by=user)

            return Response([
                {
                    "id": receipt.id,
                    "receipt_number": receipt.receipt_number,
                    "loan_id": receipt.loan_id,
                    "customer_name": receipt.loan.customer.full_name,
                    "amount": str(receipt.amount),
                    "status": receipt.status,
                    "collected_at": receipt.collected_at,
                    "collected_by": receipt.collected_by.username,
                    "branch_id": getattr(
                        getattr(receipt.collected_by, "agent_profile", None),
                        "home_branch_id",
                        None,
                    ),
                }
                for receipt in receipts
            ])

        if is_admin(user):
            submissions = CashSubmission.objects.all()
        elif is_branch_manager(user):
            manager_profile = getattr(user, "branch_manager_profile", None)
            manager_branch_id = getattr(manager_profile, "branch_id", None)
            if not manager_branch_id:
                return Response(
                    {"error": "Your account has no home branch configured."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            submissions = CashSubmission.objects.filter(branch_id=manager_branch_id)
        elif is_collection_agent(user):
            submissions = CashSubmission.objects.filter(agent=user)
        else:
            return Response(
                {"error": "Your role cannot access reconciliation."},
                status=status.HTTP_403_FORBIDDEN,
            )

        submissions = submissions.select_related(
            "agent", "branch", "verified_by"
        ).order_by("-submitted_at")
        return Response(CashSubmissionSerializer(submissions, many=True).data)

    @transaction.atomic
    def post(self, request):
        user = request.user
        admin = is_admin(user)
        manager = is_branch_manager(user)

        # Collection Agents can record collections, but the reconciliation form
        # is for Branch Managers to confirm cash deposited.
        if not (admin or manager):
            return Response(
                {"error": "Branch Manager or Administrator role required."},
                status=status.HTTP_403_FORBIDDEN,
            )

        receipt_ids = request.data.get("receipt_ids", [])
        if (
            not isinstance(receipt_ids, list)
            or not receipt_ids
            or len(receipt_ids) != len(set(map(str, receipt_ids)))
        ):
            return Response(
                {"error": "Select one or more unique collected receipt IDs."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        receipts = list(
            PaymentReceipt.objects.select_for_update()
            .filter(id__in=receipt_ids, status="COLLECTED")
            .select_related("collected_by")
        )
        if len(receipts) != len(receipt_ids):
            return Response(
                {"error": "Some receipts are invalid or have already been submitted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Branch managers reconcile only receipts collected by agents whose
        # home branch matches the manager's branch. The server determines the
        # branch from the authenticated manager profile.
        if manager:
            manager_profile = getattr(user, "branch_manager_profile", None)
            branch_id = getattr(manager_profile, "branch_id", None)
            if not branch_id:
                return Response(
                    {"error": "Your account has no home branch configured."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            allowed_receipt_ids = set(
                PaymentReceipt.objects.filter(
                    id__in=receipt_ids,
                    status="COLLECTED",
                    collected_by__agent_profile__home_branch_id=branch_id,
                ).values_list("id", flat=True)
            )
            if allowed_receipt_ids != set(receipt_ids):
                return Response(
                    {"error": "Select only collected receipts from your home branch."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            # Administrators may reconcile any branch and must choose one.
            branch_id = request.data.get("branch_id")
            if not branch_id:
                return Response(
                    {"error": "Select a branch for this reconciliation."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        expected = sum((receipt.amount for receipt in receipts), Decimal("0.00"))

        # Store the manager as the submitter in the existing agent FK field.
        # The schema's existing field is named `agent`; no migration is needed.
        submission = CashSubmission.objects.create(
            submission_reference=f"CS-{uuid.uuid4().hex[:12].upper()}",
            agent=user,
            branch_id=branch_id,
            expected_amount=expected,
            status="PENDING",
            notes="Branch Manager confirmed cash deposit.",
        )

        SubmissionReceipt.objects.bulk_create([
            SubmissionReceipt(submission=submission, receipt=receipt)
            for receipt in receipts
        ])
        PaymentReceipt.objects.filter(
            id__in=[receipt.id for receipt in receipts]
        ).update(status="SUBMITTED")

        return Response(
            CashSubmissionSerializer(submission).data,
            status=status.HTTP_201_CREATED,
        )


class CashSubmissionVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        user = request.user
        admin = is_admin(user)
        manager = is_branch_manager(user)

        if not (admin or manager):
            return Response(
                {"error": "Branch Manager or Administrator role required."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            submission = (
                CashSubmission.objects.select_for_update()
                .select_related("branch")
                .get(pk=pk)
            )
        except CashSubmission.DoesNotExist:
            return Response(
                {"error": "Submission not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if manager:
            manager_profile = getattr(user, "branch_manager_profile", None)
            manager_branch_id = getattr(manager_profile, "branch_id", None)
            if not manager_branch_id:
                return Response(
                    {"error": "Your account has no home branch configured."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if submission.branch_id != manager_branch_id:
                return Response(
                    {"error": "You can only verify reconciliations for your home branch."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        if submission.status != "PENDING":
            return Response(
                {"error": "This submission has already been reviewed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        action = request.data.get("action")
        notes = request.data.get("notes", "")
        actual = request.data.get("actual_amount")

        if action not in ["approve", "reject"]:
            return Response(
                {"error": "Action must be approve or reject."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if action == "reject":
            submission.status = "REJECTED"
            submission.notes = notes
            submission.verified_by = user
            submission.verified_at = timezone.now()
            submission.save()

            receipt_ids = submission.receipt_links.values_list("receipt_id", flat=True)
            PaymentReceipt.objects.filter(
                id__in=receipt_ids, status="SUBMITTED"
            ).update(status="COLLECTED")
            return Response(CashSubmissionSerializer(submission).data)

        if actual is None:
            return Response(
                {"error": "actual_amount is required for approval."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            actual_amount = Decimal(str(actual))
            if not actual_amount.is_finite() or actual_amount < 0:
                raise ValueError
        except (ValueError, InvalidOperation, TypeError):
            return Response(
                {"error": "actual_amount must be a valid non-negative amount."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        discrepancy = submission.expected_amount - actual_amount
        submission.actual_amount = actual_amount
        submission.discrepancy_amount = discrepancy
        submission.status = (
            "APPROVED" if discrepancy == Decimal("0.00")
            else "APPROVED_WITH_DISCREPANCY"
        )
        submission.notes = notes
        submission.verified_by = user
        submission.verified_at = timezone.now()
        submission.save()

        if actual_amount > 0:
            VaultMovement.objects.create(
                branch=submission.branch,
                movement_type="CASH_RECEIVED",
                amount=actual_amount,
                submission=submission,
                recorded_by=user,
                notes=f"Cash accepted for {submission.submission_reference}",
            )

        PaymentReceipt.objects.filter(
            submission_links__submission=submission,
            status="SUBMITTED",
        ).update(status="RECONCILED")

        return Response(CashSubmissionSerializer(submission).data)
