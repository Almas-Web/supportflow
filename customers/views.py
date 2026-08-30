from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema
from rest_framework import generics

from organizations.models import Organization
from organizations.permissions import (
    IsOrganizationAdminOrOwner,
    IsOrganizationMember,
)

from .models import Customer
from .serializers import CustomerSerializer


@extend_schema(tags=["Customers"])
class CustomerListCreateView(generics.ListCreateAPIView):
    serializer_class = CustomerSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsOrganizationAdminOrOwner()]

        return [IsOrganizationMember()]

    def get_queryset(self):
        return Customer.objects.filter(
            organization_id=self.kwargs["organization_id"],
            organization__memberships__user=self.request.user,
            organization__memberships__is_active=True,
            organization__is_active=True,
        ).select_related(
            "user",
            "organization",
        ).distinct()

    def get_serializer_context(self):
        context = super().get_serializer_context()

        context["organization"] = get_object_or_404(
            Organization,
            id=self.kwargs["organization_id"],
        )

        return context

    def perform_create(self, serializer):
        organization = get_object_or_404(
            Organization,
            id=self.kwargs["organization_id"],
        )

        serializer.save(organization=organization)


@extend_schema(tags=["Customers"])
class CustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CustomerSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsOrganizationAdminOrOwner()]

        return [IsOrganizationMember()]

    def get_queryset(self):
        return Customer.objects.filter(
            organization_id=self.kwargs["organization_id"],
            organization__memberships__user=self.request.user,
            organization__memberships__is_active=True,
            organization__is_active=True,
        ).select_related(
            "user",
            "organization",
        ).distinct()

    def get_serializer_context(self):
        context = super().get_serializer_context()

        context["organization"] = get_object_or_404(
            Organization,
            id=self.kwargs["organization_id"],
        )

        return context