from rest_framework import serializers
from organizations.models import Membership
from .models import Team, TeamMember

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ["id", "organization", "name", "slug", "description", "lead", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "organization", "created_at", "updated_at"]

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Team name cannot be empty.")
        return value.strip()

    def validate(self, attrs):
        organization_id = self.context["view"].kwargs.get("organization_id")
        organization = self.instance.organization if self.instance else None
        if organization_id:
            organization = organization or self.context["view"].kwargs.get("organization")
            if organization is None:
                from organizations.models import Organization
                organization = Organization.objects.filter(id=organization_id).first()
        lead = attrs.get("lead", getattr(self.instance, "lead", None))
        if not organization:
            raise serializers.ValidationError({"organization": "Organization not found."})
        if not organization.is_active:
            raise serializers.ValidationError({"organization": "Organization is inactive."})
        if lead:
            membership = Membership.objects.filter(organization=organization, user=lead, role=Membership.AGENT, is_active=True, organization__is_active=True).exists()
            if not membership:
                raise serializers.ValidationError({"lead": "Team lead must be an active agent of the organization."})
        if self.instance is None and Team.objects.filter(organization=organization, slug=attrs.get("slug")).exists():
            raise serializers.ValidationError({"slug": "A team with this slug already exists in this organization."})
        if self.instance and "slug" in attrs and Team.objects.filter(organization=organization, slug=attrs["slug"]).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError({"slug": "A team with this slug already exists in this organization."})
        return attrs

class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ["id", "team", "user", "is_active", "joined_at"]
        read_only_fields = ["id", "team", "joined_at"]

    def validate(self, attrs):
        team_id = self.context["view"].kwargs.get("team_id")
        organization_id = self.context["view"].kwargs.get("organization_id")
        team = Team.objects.filter(id=team_id, organization_id=organization_id).first()
        user = attrs.get("user", getattr(self.instance, "user", None))
        if not team:
            raise serializers.ValidationError({"team": "Team not found."})
        if not team.is_active:
            raise serializers.ValidationError({"team": "Team is inactive."})
        if not team.organization.is_active:
            raise serializers.ValidationError({"team": "Organization is inactive."})
        if user:
            membership = Membership.objects.filter(organization=team.organization, user=user, role=Membership.AGENT, is_active=True, organization__is_active=True).exists()
            if not membership:
                raise serializers.ValidationError({"user": "Team member must be an active agent of the organization."})
            duplicate = TeamMember.objects.filter(team=team, user=user).exclude(pk=self.instance.pk if self.instance else None).exists()
            if duplicate:
                raise serializers.ValidationError({"user": "This agent is already a member of the team."})
        return attrs