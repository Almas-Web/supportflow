from django.contrib import admin
from .models import Ticket

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ["ticket_number", "title", "organization", "customer", "team", "agent", "priority", "status", "category", "created_at", "updated_at"]
    list_filter = ["organization", "team", "agent", "priority", "status", "category", "created_at"]
    search_fields = ["ticket_number", "title", "description", "customer__user__username", "customer__user__email", "team__name", "agent__username", "agent__email"]
    readonly_fields = ["ticket_number", "created_at", "updated_at", "resolved_at"]
    autocomplete_fields = ["organization", "customer", "team", "agent"]
    ordering = ["-created_at"]
    list_per_page = 25