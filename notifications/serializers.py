from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "user", "organization", "ticket", "notification_type", "title", "message", "is_read", "created_at"]
        read_only_fields = ["id", "user", "organization", "created_at"]

    def validate(self, attrs):
        ticket = attrs.get("ticket")
        if ticket and ticket.organization_id != self.context["organization_id"]:
            raise serializers.ValidationError({"ticket": "Ticket must belong to the same organization."})
        return attrs