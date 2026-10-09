from django.conf import settings
from django.db import models


class AgentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="agent_profile",
    )
    employee_id = models.CharField(
        max_length=20,
        unique=True,
    )
    home_branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.PROTECT,
        related_name="agents",
    )
    phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee_id} - {self.user.username}"



class BranchManagerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="branch_manager_profile",
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.PROTECT,
        related_name="managers",
    )
    employee_id = models.CharField(
        max_length=20,
        unique=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee_id} - {self.user.username}"
