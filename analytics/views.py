from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from organizations.models import Membership
from .models import AnalyticsSnapshot
from .serializers import AnalyticsSnapshotSerializer
from .services import generate_analytics_snapshot

@extend_schema(tags=["Analytics"])
class AnalyticsSnapshotListCreateView(generics.ListCreateAPIView):
    serializer_class = AnalyticsSnapshotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        organization_id = self.kwargs["organization_id"]
        if not Membership.objects.filter(organization_id=organization_id, user=self.request.user, is_active=True, organization__is_active=True).exists():
            raise PermissionDenied("You do not have access to this organization.")
        return AnalyticsSnapshot.objects.filter(organization_id=organization_id)

    def perform_create(self, serializer):
        organization_id = self.kwargs["organization_id"]
        membership = get_object_or_404(Membership, organization_id=organization_id, user=self.request.user, is_active=True, organization__is_active=True)
        if membership.role not in [Membership.OWNER, Membership.ADMIN]:
            raise PermissionDenied("Only organization owners and admins can manage analytics snapshots.")
        serializer.save(organization_id=organization_id)

@extend_schema(tags=["Analytics"])
class AnalyticsSnapshotDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AnalyticsSnapshotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        organization_id = self.kwargs["organization_id"]
        if not Membership.objects.filter(organization_id=organization_id, user=self.request.user, is_active=True, organization__is_active=True).exists():
            raise PermissionDenied("You do not have access to this organization.")
        return AnalyticsSnapshot.objects.filter(organization_id=organization_id)

    def perform_update(self, serializer):
        organization_id = self.kwargs["organization_id"]
        membership = get_object_or_404(Membership, organization_id=organization_id, user=self.request.user, is_active=True, organization__is_active=True)
        if membership.role not in [Membership.OWNER, Membership.ADMIN]:
            raise PermissionDenied("Only organization owners and admins can manage analytics snapshots.")
        serializer.save()

    def perform_destroy(self, instance):
        membership = get_object_or_404(Membership, organization_id=instance.organization_id, user=self.request.user, is_active=True, organization__is_active=True)
        if membership.role not in [Membership.OWNER, Membership.ADMIN]:
            raise PermissionDenied("Only organization owners and admins can manage analytics snapshots.")
        instance.delete()

@extend_schema(tags=["Analytics"])
class TicketAnalyticsView(generics.RetrieveAPIView):
    serializer_class = AnalyticsSnapshotSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        organization_id = self.kwargs["organization_id"]
        membership = get_object_or_404(Membership, organization_id=organization_id, user=self.request.user, is_active=True, organization__is_active=True)
        return generate_analytics_snapshot(membership.organization)