from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from organizations.models import Membership
from .models import Notification
from .serializers import NotificationSerializer

@extend_schema(tags=["Notifications"])
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Authentication credentials were not provided.")
        organization_id = self.kwargs["organization_id"]
        if not Membership.objects.filter(organization_id=organization_id, user=self.request.user, is_active=True, organization__is_active=True).exists():
            raise PermissionDenied("You do not have access to this organization.")
        return Notification.objects.filter(organization_id=organization_id, user=self.request.user).select_related("organization", "ticket")

@extend_schema(tags=["Notifications"])
class NotificationDetailView(generics.RetrieveAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Authentication credentials were not provided.")
        organization_id = self.kwargs["organization_id"]
        if not Membership.objects.filter(organization_id=organization_id, user=self.request.user, is_active=True, organization__is_active=True).exists():
            raise PermissionDenied("You do not have access to this organization.")
        return Notification.objects.filter(organization_id=organization_id, user=self.request.user).select_related("organization", "ticket")

@extend_schema(tags=["Notifications"])
class NotificationMarkReadView(generics.UpdateAPIView):
    serializer_class = NotificationSerializer
    http_method_names = ["patch"]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Authentication credentials were not provided.")
        organization_id = self.kwargs["organization_id"]
        if not Membership.objects.filter(organization_id=organization_id, user=self.request.user, is_active=True, organization__is_active=True).exists():
            raise PermissionDenied("You do not have access to this organization.")
        return Notification.objects.filter(organization_id=organization_id, user=self.request.user)

    def patch(self, request, *args, **kwargs):
        notification = get_object_or_404(self.get_queryset(), pk=kwargs["pk"])
        notification.is_read = True
        notification.save(update_fields=["is_read"])
        return Response(self.get_serializer(notification).data, status=status.HTTP_200_OK)

@extend_schema(tags=["Notifications"])
class NotificationMarkAllReadView(generics.GenericAPIView):
    serializer_class = NotificationSerializer

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied("Authentication credentials were not provided.")
        organization_id = kwargs["organization_id"]
        if not Membership.objects.filter(organization_id=organization_id, user=request.user, is_active=True, organization__is_active=True).exists():
            raise PermissionDenied("You do not have access to this organization.")
        Notification.objects.filter(organization_id=organization_id, user=request.user, is_read=False).update(is_read=True)
        return Response({"detail": "All notifications marked as read."}, status=status.HTTP_200_OK)