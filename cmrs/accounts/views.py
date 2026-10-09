from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import (
    is_admin,
    is_collection_agent,
    is_branch_manager,
    is_finance_treasury,
)


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        groups = list(user.groups.values_list("name", flat=True))

        if user.is_superuser or is_admin(user):
            role = "Administrator"
        elif is_collection_agent(user):
            role = "Collection Agent"
        elif is_branch_manager(user):
            role = "Branch Manager"
        elif is_finance_treasury(user):
            role = "Finance/Treasury"
        else:
            return Response(
                {"error": "User must have exactly one supported role."},
                status=403,
            )

        # Resolve the user's branch from their database profile.
        home_branch = None

        if role == "Collection Agent":
            profile = getattr(user, "agent_profile", None)
            home_branch = getattr(profile, "home_branch", None)

        elif role == "Branch Manager":
            profile = getattr(user, "branch_manager_profile", None)
            home_branch = getattr(profile, "branch", None)

        return Response({
            "id": user.id,
            "username": user.username,
            "role": role,
            "home_branch_id": home_branch.id if home_branch else None,
            "home_branch_name": (
                home_branch.name if home_branch else None
            ),
        })