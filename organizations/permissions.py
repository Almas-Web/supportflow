from rest_framework.permissions import BasePermission

from .models import Membership


class IsOrganizationMember(BasePermission):
    def has_permission(self, request, view):
        organization_id = view.kwargs.get("organization_id") or request.data.get("organization")
        if not request.user.is_authenticated or not organization_id:
            return False
        return Membership.objects.filter(
            organization_id=organization_id,
            user=request.user,
            is_active=True,
            organization__is_active=True,
        ).exists()


class IsOrganizationOwner(BasePermission):
    def has_permission(self, request, view):
        organization_id = view.kwargs.get("organization_id") or request.data.get("organization")
        if not request.user.is_authenticated or not organization_id:
            return False
        return Membership.objects.filter(
            organization_id=organization_id,
            user=request.user,
            role=Membership.OWNER,
            is_active=True,
            organization__is_active=True,
        ).exists()


class IsOrganizationAdmin(BasePermission):
    def has_permission(self, request, view):
        organization_id = view.kwargs.get("organization_id") or request.data.get("organization")
        if not request.user.is_authenticated or not organization_id:
            return False
        return Membership.objects.filter(
            organization_id=organization_id,
            user=request.user,
            role=Membership.ADMIN,
            is_active=True,
            organization__is_active=True,
        ).exists()


class IsOrganizationAgent(BasePermission):
    def has_permission(self, request, view):
        organization_id = view.kwargs.get("organization_id") or request.data.get("organization")
        if not request.user.is_authenticated or not organization_id:
            return False
        return Membership.objects.filter(
            organization_id=organization_id,
            user=request.user,
            role=Membership.AGENT,
            is_active=True,
            organization__is_active=True,
        ).exists()


class IsOrganizationCustomer(BasePermission):
    def has_permission(self, request, view):
        organization_id = view.kwargs.get("organization_id") or request.data.get("organization")
        if not request.user.is_authenticated or not organization_id:
            return False
        return Membership.objects.filter(
            organization_id=organization_id,
            user=request.user,
            role=Membership.CUSTOMER,
            is_active=True,
            organization__is_active=True,
        ).exists()


class IsOrganizationAdminOrOwner(BasePermission):
    def has_permission(self, request, view):
        organization_id = view.kwargs.get("organization_id") or request.data.get("organization")
        if not request.user.is_authenticated or not organization_id:
            return False
        return Membership.objects.filter(
            organization_id=organization_id,
            user=request.user,
            role__in=[Membership.OWNER, Membership.ADMIN],
            is_active=True,
            organization__is_active=True,
        ).exists()