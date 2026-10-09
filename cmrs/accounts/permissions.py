from rest_framework.permissions import BasePermission


COLLECTION_AGENT = "Collection Agent"
BRANCH_MANAGER = "Branch Manager"
FINANCE_TREASURY = "Finance/Treasury"
ADMINISTRATOR = "Administrator"


def has_role(user, role):
    return (
        user.is_authenticated
        and user.groups.filter(name=role).exists()
    )


def is_admin(user):
    return (
        user.is_authenticated
        and (
            user.is_superuser
            or has_role(user, ADMINISTRATOR)
        )
    )


def is_collection_agent(user):
    return has_role(user, COLLECTION_AGENT)


def is_branch_manager(user):
    return has_role(user, BRANCH_MANAGER)


def is_finance_treasury(user):
    return has_role(user, FINANCE_TREASURY)


def can_view_all_financial_data(user):
    return is_admin(user) or is_finance_treasury(user)


class IsAdministrator(BasePermission):
    def has_permission(self, request, view):
        return is_admin(request.user)


class IsCollectionAgent(BasePermission):
    def has_permission(self, request, view):
        return is_admin(request.user) or is_collection_agent(request.user)


class IsBranchManager(BasePermission):
    def has_permission(self, request, view):
        return is_admin(request.user) or is_branch_manager(request.user)


class IsFinanceTreasury(BasePermission):
    def has_permission(self, request, view):
        return is_admin(request.user) or is_finance_treasury(request.user)
