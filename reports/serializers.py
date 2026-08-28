from rest_framework import serializers
from .models import Report

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ["id", "organization", "name", "report_type", "description", "start_date", "end_date", "data", "generated_by", "created_at", "updated_at"]
        read_only_fields = ["id", "organization", "data", "generated_by", "created_at", "updated_at"]

    def validate(self, attrs):
        start_date = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end_date = attrs.get("end_date", getattr(self.instance, "end_date", None))
        name = attrs.get("name", getattr(self.instance, "name", ""))
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({"end_date": "End date must be greater than or equal to start date."})
        if not name.strip():
            raise serializers.ValidationError({"name": "Report name cannot be empty."})
        return attrs