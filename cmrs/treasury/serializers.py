from rest_framework import serializers
from .models import BankDeposit, BankSettlement


class BankSettlementSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankSettlement
        fields = [
            "id",
            "bank_reference_number",
            "credited_amount",
            "settlement_date",
            "recorded_by",
            "notes",
            "created_at",
        ]
        read_only_fields = ["recorded_by", "created_at"]


class BankDepositSerializer(serializers.ModelSerializer):
    settlements = BankSettlementSerializer(
        source="banksettlement_set", many=True, read_only=True
    )
    total_credited = serializers.SerializerMethodField()
    outstanding_amount = serializers.SerializerMethodField()

    class Meta:
        model = BankDeposit
        fields = [
            "id",
            "deposit_reference",
            "branch",
            "bank_name",
            "bank_account_reference",
            "deposited_amount",
            "deposit_date",
            "status",
            "created_by",
            "created_at",
            "notes",
            "settlements",
            "total_credited",
            "outstanding_amount",
        ]
        read_only_fields = ["created_by", "created_at", "status"]

    def get_total_credited(self, obj):
        from decimal import Decimal
        from django.db.models import Sum

        total = obj.banksettlement_set.aggregate(
            total=Sum("credited_amount")
        )["total"]
        return str(total or Decimal("0.00"))

    def get_outstanding_amount(self, obj):
        from decimal import Decimal
        from django.db.models import Sum

        total = obj.banksettlement_set.aggregate(
            total=Sum("credited_amount")
        )["total"] or Decimal("0.00")
        return str(max(obj.deposited_amount - total, Decimal("0.00")))