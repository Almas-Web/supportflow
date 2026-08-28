from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from organizations.models import Membership
from .models import Ticket
from .serializers import TicketSerializer

class TicketListCreateView(generics.ListCreateAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        organization_id = self.kwargs["organization_id"]
        if not Membership.objects.filter(organization_id=organization_id, user=self.request.user, is_active=True, organization__is_active=True).exists():
            raise PermissionDenied("You do not have access to this organization.")
        return Ticket.objects.filter(organization_id=organization_id).select_related("organization", "customer", "team", "agent")

    def perform_create(self, serializer):
        organization_id = self.kwargs["organization_id"]
        membership = get_object_or_404(Membership, organization_id=organization_id, user=self.request.user, is_active=True, organization__is_active=True)
        if membership.role not in [Membership.OWNER, Membership.ADMIN, Membership.AGENT, Membership.CUSTOMER]:
            raise PermissionDenied("You do not have permission to create tickets.")
        serializer.save(organization_id=organization_id)

class TicketDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        organization_id = self.kwargs["organization_id"]
        if not Membership.objects.filter(organization_id=organization_id, user=self.request.user, is_active=True, organization__is_active=True).exists():
            raise PermissionDenied("You do not have access to this organization.")
        return Ticket.objects.filter(organization_id=organization_id).select_related("organization", "customer", "team", "agent")

    def perform_update(self, serializer):
        organization_id = self.kwargs["organization_id"]
        membership = get_object_or_404(Membership, organization_id=organization_id, user=self.request.user, is_active=True, organization__is_active=True)
        if membership.role == Membership.CUSTOMER and "agent" in serializer.validated_data:
            raise PermissionDenied("Customers cannot assign agents.")
        serializer.save()

    def perform_destroy(self, instance):
        membership = get_object_or_404(Membership, organization_id=instance.organization_id, user=self.request.user, is_active=True, organization__is_active=True)
        if membership.role not in [Membership.OWNER, Membership.ADMIN]:
            raise PermissionDenied("Only organization owners and admins can delete tickets.")
        instance.delete()