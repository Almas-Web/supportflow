from django.conf import settings
from django.db import models
from organizations.models import Organization

class AuditLog(models.Model):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    ACTION_CHOICES = [(CREATE, "Create"), (UPDATE, "Update"), (DELETE, "Delete"), (LOGIN, "Login"), (LOGOUT, "Logout")]
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="audit_logs")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="audit_logs")
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    description = models.TextField()
    changes = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.action} - {self.model_name}"