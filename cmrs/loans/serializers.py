
from rest_framework import serializers
from .models import Loan


class LoanSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source="customer.full_name",
        read_only=True,
    )
    total_scheduled = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = [
            "id",
            "loan_number",
            "customer",
            "customer_name",
            "principal_amount",
            "annual_interest_rate",
            "tenure_months",
            "repayment_frequency",
            "disbursement_date",
            "status",
            "total_scheduled",
        ]

    def get_total_scheduled(self, obj):
        from django.db.models import Sum
        from .models import RepaymentSchedule

        totals = RepaymentSchedule.objects.filter(
            loan=obj
        ).aggregate(
            principal=Sum("principal_due"),
            interest=Sum("interest_due"),
        )
        principal = totals["principal"] or 0
        interest = totals["interest"] or 0
        return str(principal + interest)
