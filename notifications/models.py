from django.conf import settings
from django.db import models
from organizations.models import Organization
from tickets.models import Ticket

class Notification(models.Model):
    TICKET_CREATED = "TICKET_CREATED"
    TICKET_ASSIGNED = "TICKET_ASSIGNED"
    TICKET_UPDATED = "TICKET_UPDATED"
    TICKET_STATUS_CHANGED = "TICKET_STATUS_CHANGED"
    TICKET_RESOLVED = "TICKET_RESOLVED"
    GENERAL = "GENERAL"
    NOTIFICATION_TYPE_CHOICES = [(TICKET_CREATED, "Ticket Created"), (TICKET_ASSIGNED, "Ticket Assigned"), (TICKET_UPDATED, "Ticket Updated"), (TICKET_STATUS_CHANGED, "Ticket Status Changed"), (TICKET_RESOLVED, "Ticket Resolved"), (GENERAL, "General")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="notifications")
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="notifications", blank=True, null=True)
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES, default=GENERAL)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created_at"]
    def __str__(self):
        return f"{self.user.email} - {self.title}"