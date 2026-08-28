from django.contrib import admin
from .models import SLAPolicy, TicketSLA
@admin.register(SLAPolicy)
class SLAPolicyAdmin(admin.ModelAdmin):
    list_display = ["id", "organization", "name", "priority", "first_response_minutes", "resolution_minutes", "is_active", "created_at"]
    list_filter = ["priority", "is_active", "created_at"]
    search_fields = ["name", "description", "organization__name"]
    ordering = ["organization", "priority", "name"]
    readonly_fields = ["created_at", "updated_at"]
@admin.register(TicketSLA)
class TicketSLAAdmin(admin.ModelAdmin):
    list_display = ["id", "ticket", "policy", "status", "first_response_due_at", "resolution_due_at", "first_responded_at", "resolved_at", "created_at"]
    list_filter = ["status", "policy__priority", "created_at"]
    search_fields = ["ticket__ticket_number", "ticket__title", "policy__name", "ticket__organization__name"]
    ordering = ["resolution_due_at"]
    readonly_fields = ["created_at", "updated_at"]