from django.conf import settings
from django.db import models
from organizations.models import Organization

class Customer(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="customers")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer_profiles")
    company_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["organization", "user"], name="unique_customer_per_organization"),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.organization.name}"