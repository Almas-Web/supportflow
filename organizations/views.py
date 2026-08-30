from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import Membership, Organization
from .permissions import IsOrganizationAdminOrOwner, IsOrganizationMember
from .serializers import MembershipSerializer, OrganizationSerializer

User = get_user_model()


@extend_schema(tags=["Organizations"])
class OrganizationListCreateView(generics.ListCreateAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Organization.objects.filter(
            memberships__user=self.request.user,
            memberships__is_active=True,
            is_active=True,
        ).distinct()

    def perform_create(self, serializer):
        organization = serializer.save(owner=self.request.user)
        Membership.objects.create(
            organization=organization,
            user=self.request.user,
            role=Membership.OWNER,
        )


@extend_schema(tags=["Organizations"])
class OrganizationDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Organization.objects.filter(
            memberships__user=self.request.user,
            memberships__is_active=True,
            is_active=True,
        ).distinct()


@extend_schema(tags=["Organizations"])
class MembershipListCreateView(generics.ListCreateAPIView):
    serializer_class = MembershipSerializer
    permission_classes = [IsOrganizationMember]

    def get_organization(self):
        return Organization.objects.filter(
            pk=self.kwargs["organization_id"],
            memberships__user=self.request.user,
            memberships__is_active=True,
            is_active=True,
        ).distinct().first()

    def get_queryset(self):
        organization = self.get_organization()

        if not organization:
            return Membership.objects.none()

        return Membership.objects.filter(
            organization=organization
        ).select_related("user", "organization")

    def create(self, request, *args, **kwargs):
        organization = self.get_organization()

        if not organization:
            return Response(
                {"detail": "Organization not found or you do not have permission."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not Membership.objects.filter(
            organization=organization,
            user=request.user,
            role__in=[Membership.OWNER, Membership.ADMIN],
            is_active=True,
        ).exists():
            return Response(
                {"detail": "You do not have permission to add members."},
                status=status.HTTP_403_FORBIDDEN,
            )

        user_id = request.data.get("user")
        role = request.data.get("role")

        if not user_id:
            return Response(
                {"user": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if role not in dict(Membership.ROLE_CHOICES):
            return Response(
                {"role": ["Invalid role."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if role == Membership.OWNER:
            return Response(
                {"detail": "An organization can have only one owner."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(pk=user_id).first()

        if not user:
            return Response(
                {"user": ["User not found."]},
                status=status.HTTP_404_NOT_FOUND,
            )

        if Membership.objects.filter(
            organization=organization,
            user=user,
        ).exists():
            return Response(
                {"detail": "This user is already a member of the organization."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        membership = Membership.objects.create(
            organization=organization,
            user=user,
            role=role,
        )

        return Response(
            self.get_serializer(membership).data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Organizations"])
class MembershipDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MembershipSerializer
    permission_classes = [IsOrganizationMember]

    def get_organization(self):
        return Organization.objects.filter(
            pk=self.kwargs["organization_id"],
            memberships__user=self.request.user,
            memberships__is_active=True,
            is_active=True,
        ).distinct().first()

    def get_queryset(self):
        organization = self.get_organization()

        if not organization:
            return Membership.objects.none()

        return Membership.objects.filter(
            organization=organization
        ).select_related("user", "organization")

    def update(self, request, *args, **kwargs):
        membership = self.get_object()

        if not Membership.objects.filter(
            organization=membership.organization,
            user=request.user,
            role__in=[Membership.OWNER, Membership.ADMIN],
            is_active=True,
        ).exists():
            return Response(
                {"detail": "You do not have permission to modify members."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if membership.role == Membership.OWNER:
            return Response(
                {"detail": "The organization owner cannot be modified."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        current_user_membership = Membership.objects.get(
            organization=membership.organization,
            user=request.user,
        )

        if (
            current_user_membership.role == Membership.ADMIN
            and membership.role == Membership.ADMIN
        ):
            return Response(
                {"detail": "An admin cannot modify another admin."},
                status=status.HTTP_403_FORBIDDEN,
            )

        role = request.data.get("role", membership.role)

        if role == Membership.OWNER:
            return Response(
                {"detail": "The organization owner cannot be changed through membership."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if role not in dict(Membership.ROLE_CHOICES):
            return Response(
                {"role": ["Invalid role."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        membership.role = role

        if "is_active" in request.data:
            membership.is_active = request.data["is_active"]

        membership.save(update_fields=["role", "is_active"])

        return Response(
            self.get_serializer(membership).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        membership = self.get_object()

        if not Membership.objects.filter(
            organization=membership.organization,
            user=request.user,
            role__in=[Membership.OWNER, Membership.ADMIN],
            is_active=True,
        ).exists():
            return Response(
                {"detail": "You do not have permission to remove members."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if membership.role == Membership.OWNER:
            return Response(
                {"detail": "The organization owner cannot be removed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        current_user_membership = Membership.objects.get(
            organization=membership.organization,
            user=request.user,
        )

        if (
            current_user_membership.role == Membership.ADMIN
            and membership.role == Membership.ADMIN
        ):
            return Response(
                {"detail": "An admin cannot remove another admin."},
                status=status.HTTP_403_FORBIDDEN,
            )

        membership.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)