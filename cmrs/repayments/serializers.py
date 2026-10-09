
from rest_framework import serializers


class RepaymentSerializer(serializers.Serializer):
    loan_id = serializers.IntegerField()
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0.01,
    )
