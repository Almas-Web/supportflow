from rest_framework import serializers
from organizations.models import Membership
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "organization", "user", "company_name", "phone", "address", "notes", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "organization", "created_at", "updated_at"]

    def validate(self, attrs):
        organization_id = self.context["view"].kwargs.get("organization_id")
        organization = self.instance.organization if self.instance else None
        if organization_id:
            from organizations.models import Organization
            organization = organization or Organization.objects.filter(id=organization_id).first()
        user = attrs.get("user", getattr(self.instance, "user", None))
        if not organization:
            raise serializers.ValidationError({"organization": "Organization not found."})
        if not organization.is_active:
            raise serializers.ValidationError({"organization": "Organization is inactive."})
        if user:
            membership = Membership.objects.filter(organization=organization, user=user, role=Membership.CUSTOMER, is_active=True, organization__is_active=True).exists()
            if not membership:
                raise serializers.ValidationError({"user": "Customer must have an active CUSTOMER membership in this organization."})
            duplicate = Customer.objects.filter(organization=organization, user=user).exclude(pk=self.instance.pk if self.instance else None).exists()
            if duplicate:
                raise serializers.ValidationError({"user": "This user is already a customer of this organization."})
        return attrs