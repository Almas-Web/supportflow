from django.contrib import admin

from .models import Team, TeamMember


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "lead", "is_active", "created_at", "updated_at")
    list_filter = ("is_active", "organization")
    search_fields = ("name", "slug", "organization__name", "lead__username", "lead__email")
    readonly_fields = ("created_at", "updated_at")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("-created_at",)

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("team", "user", "is_active", "joined_at")
    list_filter = ("is_active", "team__organization", "team")
    search_fields = ("team__name", "user__username", "user__email")
    readonly_fields = ("joined_at",)
    ordering = ("joined_at",)