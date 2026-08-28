from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["user", "organization", "company_name", "phone", "is_active", "created_at"]
    list_filter = ["organization", "is_active", "created_at"]
    search_fields = ["user__username", "user__email", "company_name", "phone"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]