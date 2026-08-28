from django.db import models
from organizations.models import Organization

class Report(models.Model):
    TICKET_SUMMARY = "TICKET_SUMMARY"
    SLA_PERFORMANCE = "SLA_PERFORMANCE"
    TEAM_PERFORMANCE = "TEAM_PERFORMANCE"
    CUSTOMER_ACTIVITY = "CUSTOMER_ACTIVITY"
    REPORT_TYPE_CHOICES = [(TICKET_SUMMARY, "Ticket Summary"), (SLA_PERFORMANCE, "SLA Performance"), (TEAM_PERFORMANCE, "Team Performance"), (CUSTOMER_ACTIVITY, "Customer Activity")]
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="reports")
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPE_CHOICES)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    data = models.JSONField(default=dict)
    generated_by = models.ForeignKey("account.CustomUser", on_delete=models.PROTECT, related_name="generated_reports")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.organization.name}"