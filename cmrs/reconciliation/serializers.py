from rest_framework import serializers
from .models import CashSubmission


class CashSubmissionSerializer(serializers.ModelSerializer):
    agent_username = serializers.CharField(
        source="agent.username", read_only=True
    )
    branch_name = serializers.CharField(
        source="branch.name", read_only=True
    )

    class Meta:
        model = CashSubmission
        fields = [
            "id",
            "submission_reference",
            "agent",
            "agent_username",
            "branch",
            "branch_name",
            "expected_amount",
            "actual_amount",
            "discrepancy_amount",
            "status",
            "submitted_at",
            "verified_at",
            "verified_by",
            "notes",
        ]
        read_only_fields = [
            "submission_reference",
            "agent",
            "expected_amount",
            "discrepancy_amount",
            "status",
            "submitted_at",
            "verified_at",
            "verified_by",
        ]
