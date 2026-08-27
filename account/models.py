from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    AGENT = "AGENT"
    CUSTOMER = "CUSTOMER"
    ROLE_CHOICES = [(OWNER, "Owner"), (ADMIN, "Admin"), (AGENT, "Agent"), (CUSTOMER, "Customer")]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=CUSTOMER)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=64, blank=True, null=True)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to="profile_images/", blank=True, null=True)
    