from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "organization", "ticket", "notification_type", "title", "is_read", "created_at"]
    list_filter = ["notification_type", "is_read", "organization", "created_at"]
    search_fields = ["user__email", "title", "message", "ticket__ticket_number"]
    readonly_fields = ["created_at"]
    ordering = ["-created_at"]