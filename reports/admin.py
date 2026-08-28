from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "report_type", "start_date", "end_date", "generated_by", "created_at"]
    list_filter = ["report_type", "start_date", "end_date", "created_at"]
    search_fields = ["name", "description", "organization__name", "generated_by__username", "generated_by__email"]
    readonly_fields = ["data", "generated_by", "created_at", "updated_at"]
    ordering = ["-created_at"]