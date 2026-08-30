from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from customers.models import Customer
from organizations.models import Membership
from .models import Rating
from .serializers import RatingSerializer

@extend_schema(tags=["Ratings"])
class RatingListCreateView(generics.ListCreateAPIView):
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        organization_id = self.kwargs["organization_id"]
        if not Membership.objects.filter(organization_id=organization_id, user=self.request.user, is_active=True, organization__is_active=True).exists():
            raise PermissionDenied("You do not have access to this organization.")
        return Rating.objects.filter(organization_id=organization_id).select_related("organization", "ticket", "customer", "agent")

    def perform_create(self, serializer):
        organization_id = self.kwargs["organization_id"]
        membership = get_object_or_404(Membership, organization_id=organization_id, user=self.request.user, is_active=True, organization__is_active=True)
        if membership.role != Membership.CUSTOMER:
            raise PermissionDenied("Only customers can create ratings.")
        customer = get_object_or_404(Customer, user=self.request.user, organization_id=organization_id, is_active=True)
        ticket = serializer.validated_data["ticket"]
        if ticket.organization_id != organization_id:
            raise PermissionDenied("You cannot rate a ticket from another organization.")
        if ticket.customer_id != customer.id:
            raise PermissionDenied("You can only rate your own tickets.")
        serializer.save(organization_id=organization_id, customer=customer, agent=ticket.agent)

@extend_schema(tags=["Ratings"])
class RatingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        organization_id = self.kwargs["organization_id"]
        if not Membership.objects.filter(organization_id=organization_id, user=self.request.user, is_active=True, organization__is_active=True).exists():
            raise PermissionDenied("You do not have access to this organization.")
        return Rating.objects.filter(organization_id=organization_id).select_related("organization", "ticket", "customer", "agent")

    def perform_update(self, serializer):
        if serializer.instance.customer.user_id != self.request.user.id:
            raise PermissionDenied("You can only update your own rating.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.customer.user_id != self.request.user.id:
            raise PermissionDenied("You can only delete your own rating.")
        instance.delete()