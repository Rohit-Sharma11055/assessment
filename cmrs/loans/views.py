from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import Loan
from .serializers import LoanSerializer
from accounts.permissions import (
    is_admin,
    is_collection_agent,
    is_branch_manager,
    is_finance_treasury,
)


class LoanListView(ListAPIView):
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        loans = Loan.objects.select_related("customer")

        # Administrator and Finance/Treasury: all loans
        if is_admin(user) or is_finance_treasury(user):
            return loans.order_by("loan_number")

        # Branch Manager: loans for customers in their branch
        if is_branch_manager(user):
            profile = getattr(user, "branch_manager_profile", None)

            if not profile or not profile.branch_id:
                return loans.none()

            return loans.filter(
                customer__assignments__agent__agent_profile__home_branch_id=profile.branch_id,
                customer__assignments__is_active=True,
            ).distinct().order_by("loan_number")

        # Collection Agent: loans for currently assigned customers
        if is_collection_agent(user):
            return loans.filter(
                customer__assignments__agent=user,
                customer__assignments__is_active=True,
            ).distinct().order_by("loan_number")

        # Any unrecognized role: deny access
        raise PermissionDenied(
            "Your role does not have permission to view loans."
        )