from rest_framework.permissions import BasePermission
from organizations.models import Membership
from .models import Team, TeamMember

class IsTeamMember(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        team_id = view.kwargs.get("team_id") or view.kwargs.get("pk") or request.data.get("team")
        if not team_id:
            return False
        return TeamMember.objects.filter(team_id=team_id, user=request.user, is_active=True, team__is_active=True, team__organization__is_active=True).exists()

class IsTeamAdminOrOwner(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        organization_id = view.kwargs.get("organization_id") or request.data.get("organization")
        if not organization_id:
            team_id = view.kwargs.get("team_id") or view.kwargs.get("pk") or request.data.get("team")
            if team_id:
                organization_id = Team.objects.filter(id=team_id).values_list("organization_id", flat=True).first()
        if not organization_id:
            return False
        return Membership.objects.filter(organization_id=organization_id, user=request.user, role__in=[Membership.OWNER, Membership.ADMIN], is_active=True, organization__is_active=True).exists()

class IsTeamOwner(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        organization_id = view.kwargs.get("organization_id") or request.data.get("organization")
        if not organization_id:
            team_id = view.kwargs.get("team_id") or view.kwargs.get("pk") or request.data.get("team")
            if team_id:
                organization_id = Team.objects.filter(id=team_id).values_list("organization_id", flat=True).first()
        if not organization_id:
            return False
        return Membership.objects.filter(organization_id=organization_id, user=request.user, role=Membership.OWNER, is_active=True, organization__is_active=True).exists()
    