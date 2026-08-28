from rest_framework import serializers

from .models import Rating


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ["id", "organization", "ticket", "customer", "agent", "score", "comment", "created_at", "updated_at"]
        read_only_fields = ["id", "organization", "customer", "agent", "created_at", "updated_at"]

    def validate_score(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating score must be between 1 and 5.")
        return value

    def validate(self, attrs):
        ticket = attrs.get("ticket", getattr(self.instance, "ticket", None))

        if not ticket:
            raise serializers.ValidationError({"ticket": "Ticket is required."})

        if ticket.status not in ["RESOLVED", "CLOSED"]:
            raise serializers.ValidationError({"ticket": "Only resolved or closed tickets can be rated."})

        if not ticket.agent:
            raise serializers.ValidationError({"ticket": "Only tickets assigned to an agent can be rated."})

        if self.instance is None and Rating.objects.filter(ticket=ticket).exists():
            raise serializers.ValidationError({"ticket": "This ticket has already been rated."})

        return attrs