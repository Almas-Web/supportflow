from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from organizations.models import Membership
from .models import SLAPolicy, TicketSLA
from .serializers import SLAPolicySerializer, TicketSLASerializer

@extend_schema(tags=["SLA"])
class SLAPolicyListCreateView(generics.ListCreateAPIView):
    serializer_class = SLAPolicySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        organization_id = self.kwargs["organization_id"]
        if not Membership.objects.filter(organization_id=organization_id, user=self.request.user, is_active=True, organization__is_active=True).exists():
            raise PermissionDenied("You do not have access to this organization.")
        return SLAPolicy.objects.filter(organization_id=organization_id).select_related("organization")

    def perform_create(self, serializer):
        organization_id = self.kwargs["organization_id"]
        membership = get_object_or_404(Membership, organization_id=organization_id, user=self.request.user, is_active=True, organization__is_active=True)
        if membership.role not in [Membership.OWNER, Membership.ADMIN]:
            raise PermissionDenied("Only organization owners and admins can manage SLA policies.")
        serializer.save(organization_id=organization_id)

@extend_schema(tags=["SLA"])
class SLAPolicyDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SLAPolicySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        organization_id = self.kwargs["organization_id"]
        if not Membership.objects.filter(organization_id=organization_id, user=self.request.user, is_active=True, organization__is_active=True).exists():
            raise PermissionDenied("You do not have access to this organization.")
        return SLAPolicy.objects.filter(organization_id=organization_id).select_related("organization")

    def perform_update(self, serializer):
        organization_id = self.kwargs["organization_id"]
        membership = get_object_or_404(Membership, organization_id=organization_id, user=self.request.user, is_active=True, organization__is_active=True)
        if membership.role not in [Membership.OWNER, Membership.ADMIN]:
            raise PermissionDenied("Only organization owners and admins can manage SLA policies.")
        serializer.save()

    def perform_destroy(self, instance):
        membership = get_object_or_404(Membership, organization_id=instance.organization_id, user=self.request.user, is_active=True, organization__is_active=True)
        if membership.role not in [Membership.OWNER, Membership.ADMIN]:
            raise PermissionDenied("Only organization owners and admins can manage SLA policies.")
        instance.delete()

@extend_schema(tags=["SLA"])
class TicketSLAListCreateView(generics.ListCreateAPIView):
    serializer_class = TicketSLASerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        organization_id = self.kwargs["organization_id"]
        if not Membership.objects.filter(organization_id=organization_id, user=self.request.user, is_active=True, organization__is_active=True).exists():
            raise PermissionDenied("You do not have access to this organization.")
        return TicketSLA.objects.filter(ticket__organization_id=organization_id).select_related("ticket", "policy", "ticket__organization")

    def perform_create(self, serializer):
        organization_id = self.kwargs["organization_id"]
        membership = get_object_or_404(Membership, organization_id=organization_id, user=self.request.user, is_active=True, organization__is_active=True)
        if membership.role not in [Membership.OWNER, Membership.ADMIN]:
            raise PermissionDenied("Only organization owners and admins can manage ticket SLAs.")
        ticket = serializer.validated_data["ticket"]
        policy = serializer.validated_data["policy"]
        if ticket.organization_id != organization_id:
            raise PermissionDenied("Ticket does not belong to this organization.")
        if policy.organization_id != organization_id:
            raise PermissionDenied("SLA policy does not belong to this organization.")
        if TicketSLA.objects.filter(ticket=ticket).exists():
            raise PermissionDenied("This ticket already has an SLA.")
        serializer.save()

@extend_schema(tags=["SLA"])
class TicketSLADetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TicketSLASerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        organization_id = self.kwargs["organization_id"]
        if not Membership.objects.filter(organization_id=organization_id, user=self.request.user, is_active=True, organization__is_active=True).exists():
            raise PermissionDenied("You do not have access to this organization.")
        return TicketSLA.objects.filter(ticket__organization_id=organization_id).select_related("ticket", "policy", "ticket__organization")

    def perform_update(self, serializer):
        organization_id = self.kwargs["organization_id"]
        membership = get_object_or_404(Membership, organization_id=organization_id, user=self.request.user, is_active=True, organization__is_active=True)
        if membership.role not in [Membership.OWNER, Membership.ADMIN]:
            raise PermissionDenied("Only organization owners and admins can manage ticket SLAs.")
        ticket = serializer.validated_data.get("ticket", serializer.instance.ticket)
        policy = serializer.validated_data.get("policy", serializer.instance.policy)
        if ticket.organization_id != organization_id:
            raise PermissionDenied("Ticket does not belong to this organization.")
        if policy.organization_id != organization_id:
            raise PermissionDenied("SLA policy does not belong to this organization.")
        serializer.save()

    def perform_destroy(self, instance):
        membership = get_object_or_404(Membership, organization_id=instance.ticket.organization_id, user=self.request.user, is_active=True, organization__is_active=True)
        if membership.role not in [Membership.OWNER, Membership.ADMIN]:
            raise PermissionDenied("Only organization owners and admins can manage ticket SLAs.")
        instance.delete()