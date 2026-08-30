from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from organizations.models import Membership
from audit.models import AuditLog
from audit.services import create_audit_log

from .models import Ticket
from .serializers import TicketSerializer


@extend_schema(tags=["Tickets"])
class TicketListCreateView(generics.ListCreateAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        organization_id = self.kwargs["organization_id"]

        if not Membership.objects.filter(
            organization_id=organization_id,
            user=self.request.user,
            is_active=True,
            organization__is_active=True,
        ).exists():
            raise PermissionDenied(
                "You do not have access to this organization."
            )

        return Ticket.objects.filter(
            organization_id=organization_id,
        ).select_related(
            "organization",
            "customer",
            "team",
            "agent",
        )

    def perform_create(self, serializer):
        organization_id = self.kwargs["organization_id"]

        membership = get_object_or_404(
            Membership,
            organization_id=organization_id,
            user=self.request.user,
            is_active=True,
            organization__is_active=True,
        )

        if membership.role not in [
            Membership.OWNER,
            Membership.ADMIN,
            Membership.AGENT,
            Membership.CUSTOMER,
        ]:
            raise PermissionDenied(
                "You do not have permission to create tickets."
            )

        ticket = serializer.save(
            organization_id=organization_id,
        )

        create_audit_log(
            user=self.request.user,
            organization=ticket.organization,
            action=AuditLog.CREATE,
            model_name="Ticket",
            object_id=ticket.id,
            description=f"Created ticket {ticket.ticket_number}",
            changes={
                "title": ticket.title,
                "status": ticket.status,
                "priority": ticket.priority,
            },
        )


@extend_schema(tags=["Tickets"])
class TicketDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        organization_id = self.kwargs["organization_id"]

        if not Membership.objects.filter(
            organization_id=organization_id,
            user=self.request.user,
            is_active=True,
            organization__is_active=True,
        ).exists():
            raise PermissionDenied(
                "You do not have access to this organization."
            )

        return Ticket.objects.filter(
            organization_id=organization_id,
        ).select_related(
            "organization",
            "customer",
            "team",
            "agent",
        )

    def perform_update(self, serializer):
        organization_id = self.kwargs["organization_id"]

        membership = get_object_or_404(
            Membership,
            organization_id=organization_id,
            user=self.request.user,
            is_active=True,
            organization__is_active=True,
        )

        if (
            membership.role == Membership.CUSTOMER
            and "agent" in serializer.validated_data
        ):
            raise PermissionDenied(
                "Customers cannot assign agents."
            )

        ticket = serializer.instance

        old_values = {
            "title": ticket.title,
            "status": ticket.status,
            "priority": ticket.priority,
            "category": ticket.category,
            "team_id": ticket.team_id,
            "agent_id": ticket.agent_id,
        }

        serializer.save()

        changes = {
            "before": old_values,
            "after": {
                "title": ticket.title,
                "status": ticket.status,
                "priority": ticket.priority,
                "category": ticket.category,
                "team_id": ticket.team_id,
                "agent_id": ticket.agent_id,
            },
        }

        create_audit_log(
            user=self.request.user,
            organization=ticket.organization,
            action=AuditLog.UPDATE,
            model_name="Ticket",
            object_id=ticket.id,
            description=f"Updated ticket {ticket.ticket_number}",
            changes=changes,
        )

    def perform_destroy(self, instance):
        membership = get_object_or_404(
            Membership,
            organization_id=instance.organization_id,
            user=self.request.user,
            is_active=True,
            organization__is_active=True,
        )

        if membership.role not in [
            Membership.OWNER,
            Membership.ADMIN,
        ]:
            raise PermissionDenied(
                "Only organization owners and admins can delete tickets."
            )

        ticket_number = instance.ticket_number
        ticket_id = instance.id
        organization = instance.organization

        create_audit_log(
            user=self.request.user,
            organization=organization,
            action=AuditLog.DELETE,
            model_name="Ticket",
            object_id=ticket_id,
            description=f"Deleted ticket {ticket_number}",
            changes={
                "ticket_number": ticket_number,
                "title": instance.title,
            },
        )

        instance.delete()