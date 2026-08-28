from django.contrib import admin

from .models import Rating


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ["ticket", "customer", "agent", "score", "organization", "created_at"]
    list_filter = ["score", "organization", "created_at"]
    search_fields = ["ticket__ticket_number", "ticket__title", "customer__company_name", "agent__username"]
    readonly_fields = ["created_at", "updated_at"]