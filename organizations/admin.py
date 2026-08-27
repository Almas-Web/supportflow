from django.contrib import admin
from .models import Membership, Organization

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "owner", "is_active", "created_at")
    search_fields = ("name", "slug", "owner__username", "owner__email")
    list_filter = ("is_active",)
    readonly_fields = ("created_at", "updated_at")

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("organization", "user", "role", "is_active", "joined_at")
    search_fields = ("organization__name", "user__username", "user__email")
    list_filter = ("role", "is_active")
    readonly_fields = ("joined_at",)