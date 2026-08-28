from django.contrib import admin
from .models import AnalyticsSnapshot

@admin.register(AnalyticsSnapshot)
class AnalyticsSnapshotAdmin(admin.ModelAdmin):
    list_display = ["organization", "date", "total_tickets", "open_tickets", "in_progress_tickets", "resolved_tickets", "closed_tickets", "average_resolution_minutes", "created_at"]
    list_filter = ["organization", "date"]
    search_fields = ["organization__name"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-date"]