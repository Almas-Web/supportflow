from django.db import models
from organizations.models import Organization

class AnalyticsSnapshot(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="analytics_snapshots")
    date = models.DateField()
    total_tickets = models.PositiveIntegerField(default=0)
    open_tickets = models.PositiveIntegerField(default=0)
    in_progress_tickets = models.PositiveIntegerField(default=0)
    waiting_customer_tickets = models.PositiveIntegerField(default=0)
    resolved_tickets = models.PositiveIntegerField(default=0)
    closed_tickets = models.PositiveIntegerField(default=0)
    urgent_tickets = models.PositiveIntegerField(default=0)
    high_priority_tickets = models.PositiveIntegerField(default=0)
    average_resolution_minutes = models.FloatField(null=True, blank=True)
    tickets_by_category = models.JSONField(default=dict, blank=True)
    tickets_by_priority = models.JSONField(default=dict, blank=True)
    tickets_by_status = models.JSONField(default=dict, blank=True)
    tickets_by_team = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]
        constraints = [models.UniqueConstraint(fields=["organization", "date"], name="unique_analytics_snapshot_per_organization_date")]

    def __str__(self):
        return f"{self.organization.name} - {self.date}"