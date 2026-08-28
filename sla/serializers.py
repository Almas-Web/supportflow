from rest_framework import serializers
from tickets.models import Ticket
from .models import SLAPolicy, TicketSLA
class SLAPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = SLAPolicy
        fields = ["id", "organization", "name", "description", "priority", "first_response_minutes", "resolution_minutes", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
    def validate(self, attrs):
        organization = attrs.get("organization", getattr(self.instance, "organization", None))
        if not organization:
            raise serializers.ValidationError({"organization": "Organization is required."})
        if not organization.is_active:
            raise serializers.ValidationError({"organization": "Organization must be active."})
        if attrs.get("first_response_minutes", getattr(self.instance, "first_response_minutes", 0)) <= 0:
            raise serializers.ValidationError({"first_response_minutes": "First response time must be greater than zero."})
        if attrs.get("resolution_minutes", getattr(self.instance, "resolution_minutes", 0)) <= 0:
            raise serializers.ValidationError({"resolution_minutes": "Resolution time must be greater than zero."})
        return attrs
class TicketSLASerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketSLA
        fields = ["id", "ticket", "policy", "first_response_due_at", "resolution_due_at", "first_responded_at", "resolved_at", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
    def validate(self, attrs):
        ticket = attrs.get("ticket", getattr(self.instance, "ticket", None))
        policy = attrs.get("policy", getattr(self.instance, "policy", None))
        if not ticket:
            raise serializers.ValidationError({"ticket": "Ticket is required."})
        if not policy:
            raise serializers.ValidationError({"policy": "SLA policy is required."})
        if ticket.organization_id != policy.organization_id:
            raise serializers.ValidationError({"policy": "SLA policy must belong to the same organization as the ticket."})
        if not policy.is_active:
            raise serializers.ValidationError({"policy": "SLA policy must be active."})
        if ticket.priority != policy.priority:
            raise serializers.ValidationError({"policy": "SLA policy priority must match the ticket priority."})
        return attrs