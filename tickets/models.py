from django.conf import settings
from django.db import models
from customers.models import Customer
from organizations.models import Organization
from teams.models import Team

class Ticket(models.Model):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"
    PRIORITY_CHOICES = [(LOW, "Low"), (MEDIUM, "Medium"), (HIGH, "High"), (URGENT, "Urgent")]
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING_CUSTOMER = "WAITING_CUSTOMER"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    STATUS_CHOICES = [(OPEN, "Open"), (IN_PROGRESS, "In Progress"), (WAITING_CUSTOMER, "Waiting Customer"), (RESOLVED, "Resolved"), (CLOSED, "Closed")]
    GENERAL = "GENERAL"
    TECHNICAL = "TECHNICAL"
    BILLING = "BILLING"
    ACCOUNT = "ACCOUNT"
    OTHER = "OTHER"
    CATEGORY_CHOICES = [(GENERAL, "General"), (TECHNICAL, "Technical"), (BILLING, "Billing"), (ACCOUNT, "Account"), (OTHER, "Other")]
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="tickets")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="tickets")
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="tickets", blank=True, null=True)
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="assigned_tickets", blank=True, null=True)
    ticket_number = models.CharField(max_length=20, unique=True, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=GENERAL)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=MEDIUM)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            last_ticket = Ticket.objects.order_by("-id").first()
            next_number = (last_ticket.id + 1) if last_ticket else 1
            self.ticket_number = f"TKT-{next_number:06d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_number} - {self.title}"