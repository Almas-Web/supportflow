from django.db import models
from organizations.models import Organization
from tickets.models import Ticket
class SLAPolicy(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="sla_policies")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=Ticket.PRIORITY_CHOICES)
    first_response_minutes = models.PositiveIntegerField()
    resolution_minutes = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["priority", "name"]
        constraints = [
            models.UniqueConstraint(fields=["organization", "name"], name="unique_sla_policy_name_per_organization")
        ]
    def __str__(self):
        return f"{self.organization.name} - {self.name}"
class TicketSLA(models.Model):
    ON_TRACK = "ON_TRACK"
    BREACHED = "BREACHED"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    STATUS_CHOICES = [
        (ON_TRACK, "On Track"),
        (BREACHED, "Breached"),
        (PAUSED, "Paused"),
        (COMPLETED, "Completed"),
    ]
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name="sla")
    policy = models.ForeignKey(SLAPolicy, on_delete=models.PROTECT, related_name="ticket_slas")
    first_response_due_at = models.DateTimeField()
    resolution_due_at = models.DateTimeField()
    first_responded_at = models.DateTimeField(blank=True, null=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=ON_TRACK)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["resolution_due_at"]
    def __str__(self):
        return f"{self.ticket.ticket_number} - {self.policy.name}"