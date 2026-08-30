from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from organizations.models import Membership
from .models import AuditLog
from .serializers import AuditLogSerializer

@extend_schema(tags=["Audit"])
class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        organization_id = self.kwargs["organization_id"]
        if not Membership.objects.filter(organization_id=organization_id, user=self.request.user, is_active=True, organization__is_active=True).exists():
            raise PermissionDenied("You do not have access to this organization.")
        return AuditLog.objects.filter(organization_id=organization_id).select_related("organization", "user")

@extend_schema(tags=["Audit"])
class AuditLogDetailView(generics.RetrieveAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        organization_id = self.kwargs["organization_id"]
        if not Membership.objects.filter(organization_id=organization_id, user=self.request.user, is_active=True, organization__is_active=True).exists():
            raise PermissionDenied("You do not have access to this organization.")
        return AuditLog.objects.filter(organization_id=organization_id).select_related("organization", "user")