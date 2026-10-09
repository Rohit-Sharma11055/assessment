from django.contrib import admin
from .models import AgentProfile


@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "employee_id",
        "user",
        "home_branch",
        "phone",
    )
    search_fields = (
        "employee_id",
        "user__username",
    )
    list_filter = ("home_branch",)


from .models import BranchManagerProfile


@admin.register(BranchManagerProfile)
class BranchManagerProfileAdmin(admin.ModelAdmin):
    list_display = ("employee_id", "user", "branch")
    search_fields = ("employee_id", "user__username")
    list_filter = ("branch",)
