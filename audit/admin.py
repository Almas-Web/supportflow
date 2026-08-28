from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["user", "organization", "action", "model_name", "object_id", "created_at"]
    list_filter = ["action", "model_name", "organization", "created_at"]
    search_fields = ["user__username", "user__email", "description", "model_name"]
    readonly_fields = ["organization", "user", "action", "model_name", "object_id", "description", "changes", "created_at"]