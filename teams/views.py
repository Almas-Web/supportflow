from rest_framework import generics
from organizations.models import Organization
from organizations.permissions import IsOrganizationMember, IsOrganizationAdminOrOwner
from .models import Team, TeamMember
from .serializers import TeamSerializer, TeamMemberSerializer

class TeamListCreateView(generics.ListCreateAPIView):
    serializer_class = TeamSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permission() for permission in [IsOrganizationAdminOrOwner]]
        return [permission() for permission in [IsOrganizationMember]]

    def get_queryset(self):
        return Team.objects.filter(organization_id=self.kwargs["organization_id"], organization__memberships__user=self.request.user, organization__memberships__is_active=True, organization__is_active=True).distinct()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["organization"] = Organization.objects.filter(id=self.kwargs["organization_id"]).first()
        return context

    def perform_create(self, serializer):
        organization = Organization.objects.get(id=self.kwargs["organization_id"])
        serializer.save(organization=organization)

class TeamDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TeamSerializer

    def get_permissions(self):
        if self.request.method in ["PATCH", "PUT", "DELETE"]:
            return [permission() for permission in [IsOrganizationAdminOrOwner]]
        return [permission() for permission in [IsOrganizationMember]]

    def get_queryset(self):
        return Team.objects.filter(organization_id=self.kwargs["organization_id"], organization__memberships__user=self.request.user, organization__memberships__is_active=True, organization__is_active=True).distinct()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["organization"] = Organization.objects.filter(id=self.kwargs["organization_id"]).first()
        return context

class TeamMemberListCreateView(generics.ListCreateAPIView):
    serializer_class = TeamMemberSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permission() for permission in [IsOrganizationAdminOrOwner]]
        return [permission() for permission in [IsOrganizationMember]]

    def get_queryset(self):
        return TeamMember.objects.filter(team_id=self.kwargs["team_id"], team__organization_id=self.kwargs["organization_id"], team__organization__memberships__user=self.request.user, team__organization__memberships__is_active=True, team__is_active=True, team__organization__is_active=True).distinct()

    def perform_create(self, serializer):
        team = Team.objects.get(id=self.kwargs["team_id"], organization_id=self.kwargs["organization_id"])
        serializer.save(team=team)

class TeamMemberDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TeamMemberSerializer

    def get_permissions(self):
        if self.request.method in ["PATCH", "PUT", "DELETE"]:
            return [permission() for permission in [IsOrganizationAdminOrOwner]]
        return [permission() for permission in [IsOrganizationMember]]

    def get_queryset(self):
        return TeamMember.objects.filter(team_id=self.kwargs["team_id"], team__organization_id=self.kwargs["organization_id"], team__organization__memberships__user=self.request.user, team__organization__memberships__is_active=True, team__is_active=True, team__organization__is_active=True).distinct()