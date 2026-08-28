from rest_framework import serializers
from account.models import CustomUser
from customers.models import Customer
from teams.models import Team, TeamMember
from .models import Ticket

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "organization", "customer", "team", "agent", "ticket_number", "title", "description", "category", "priority", "status", "created_at", "updated_at", "resolved_at"]
        read_only_fields = ["id", "ticket_number", "created_at", "updated_at", "resolved_at"]

    def validate(self, attrs):
        organization = attrs.get("organization", getattr(self.instance, "organization", None))
        customer = attrs.get("customer", getattr(self.instance, "customer", None))
        team = attrs.get("team", getattr(self.instance, "team", None))
        agent = attrs.get("agent", getattr(self.instance, "agent", None))
        if not organization:
            raise serializers.ValidationError({"organization": "Organization is required."})
        if not organization.is_active:
            raise serializers.ValidationError({"organization": "Organization must be active."})
        if customer and (customer.organization_id != organization.id or not customer.is_active):
            raise serializers.ValidationError({"customer": "Customer must belong to the active organization and be active."})
        if team and (team.organization_id != organization.id or not team.is_active):
            raise serializers.ValidationError({"team": "Team must belong to the active organization and be active."})
        if agent:
            if not agent.is_active or not agent.organization_memberships.filter(organization=organization, role=CustomUser.AGENT, is_active=True).exists():
                raise serializers.ValidationError({"agent": "Agent must be an active agent of the organization."})
            if team and not TeamMember.objects.filter(team=team, user=agent, is_active=True).exists():
                raise serializers.ValidationError({"agent": "Agent must be an active member of the selected team."})
        return attrs