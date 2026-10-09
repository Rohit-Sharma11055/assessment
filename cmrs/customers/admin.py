from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "customer_number",
        "full_name",
        "phone",
        "is_active",
        "created_at",
    )
    search_fields = (
        "customer_number",
        "full_name",
        "phone",
    )
    list_filter = ("is_active",)



from .models import CustomerAssignment


@admin.register(CustomerAssignment)
class CustomerAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "customer",
        "agent",
        "assigned_at",
        "ended_at",
        "is_active",
    )
    list_filter = ("is_active", "assigned_at")
    search_fields = (
        "customer__customer_number",
        "customer__full_name",
        "agent__username",
    )
