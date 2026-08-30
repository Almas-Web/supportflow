from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from organizations.models import Membership
from .models import Report
from .serializers import ReportSerializer
from .services import generate_report_data

@extend_schema(tags=["Reports"])
class ReportListCreateView(generics.ListCreateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        organization_id = self.kwargs["organization_id"]
        if not Membership.objects.filter(organization_id=organization_id, user=self.request.user, is_active=True, organization__is_active=True).exists():
            raise PermissionDenied("You do not have access to this organization.")
        return Report.objects.filter(organization_id=organization_id).select_related("organization", "generated_by")

    def perform_create(self, serializer):
        organization_id = self.kwargs["organization_id"]
        membership = get_object_or_404(Membership, organization_id=organization_id, user=self.request.user, is_active=True, organization__is_active=True)
        if membership.role not in [Membership.OWNER, Membership.ADMIN]:
            raise PermissionDenied("Only organization owners and admins can generate reports.")
        data = generate_report_data(membership.organization, serializer.validated_data["report_type"], serializer.validated_data["start_date"], serializer.validated_data["end_date"])
        serializer.save(organization=membership.organization, generated_by=self.request.user, data=data)

@extend_schema(tags=["Reports"])
class ReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        organization_id = self.kwargs["organization_id"]
        if not Membership.objects.filter(organization_id=organization_id, user=self.request.user, is_active=True, organization__is_active=True).exists():
            raise PermissionDenied("You do not have access to this organization.")
        return Report.objects.filter(organization_id=organization_id).select_related("organization", "generated_by")

    def perform_update(self, serializer):
        organization_id = self.kwargs["organization_id"]
        membership = get_object_or_404(Membership, organization_id=organization_id, user=self.request.user, is_active=True, organization__is_active=True)
        if membership.role not in [Membership.OWNER, Membership.ADMIN]:
            raise PermissionDenied("Only organization owners and admins can update reports.")
        serializer.save()

    def perform_destroy(self, instance):
        membership = get_object_or_404(Membership, organization_id=instance.organization_id, user=self.request.user, is_active=True, organization__is_active=True)
        if membership.role not in [Membership.OWNER, Membership.ADMIN]:
            raise PermissionDenied("Only organization owners and admins can delete reports.")
        instance.delete()