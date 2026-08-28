from rest_framework import serializers
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ["id", "organization", "user", "action", "model_name", "object_id", "description", "changes", "created_at"]
        read_only_fields = ["id", "organization", "user", "action", "model_name", "object_id", "description", "changes", "created_at"]
        