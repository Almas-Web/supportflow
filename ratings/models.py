from django.conf import settings
from django.db import models
from customers.models import Customer
from organizations.models import Organization
from tickets.models import Ticket

class Rating(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="ratings")
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name="rating")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="ratings")
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="received_ratings")
    score = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.ticket.ticket_number} - {self.score}/5"