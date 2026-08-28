from rest_framework import serializers
from .models import AnalyticsSnapshot

class AnalyticsSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsSnapshot
        fields = ["id", "organization", "date", "total_tickets", "open_tickets", "in_progress_tickets", "waiting_customer_tickets", "resolved_tickets", "closed_tickets", "urgent_tickets", "high_priority_tickets", "average_resolution_minutes", "tickets_by_category", "tickets_by_priority", "tickets_by_status", "tickets_by_team", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]