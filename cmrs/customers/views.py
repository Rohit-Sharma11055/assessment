from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import Customer
from .serializers import CustomerSerializer
from accounts.permissions import (
    is_admin,
    is_collection_agent,
    is_branch_manager,
    is_finance_treasury,
)


class CustomerListView(ListAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Administrator: all customers
        if is_admin(user):
            return Customer.objects.all().order_by("customer_number")

        # Finance/Treasury: all customers
        if is_finance_treasury(user):
            return Customer.objects.all().order_by("customer_number")

        # Branch Manager: customers assigned to agents in their branch
        if is_branch_manager(user):
            profile = getattr(user, "branch_manager_profile", None)

            if not profile or not profile.branch_id:
                return Customer.objects.none()

            return Customer.objects.filter(
                assignments__agent__agent_profile__home_branch_id=profile.branch_id,
                assignments__is_active=True,
            ).distinct().order_by("customer_number")

        # Collection Agent: only currently assigned customers
        if is_collection_agent(user):
            return Customer.objects.filter(
                assignments__agent=user,
                assignments__is_active=True,
            ).distinct().order_by("customer_number")

        # No access for any other role
        raise PermissionDenied(
            "Your role does not have permission to view customers."
        )
