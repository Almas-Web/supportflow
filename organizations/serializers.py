from django.utils.text import slugify
from rest_framework import serializers
from .models import Organization

class OrganizationSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.id")

    class Meta:
        model = Organization
        fields = ["id", "name", "slug", "owner", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Organization name cannot be empty.")
        return value

    def validate_slug(self, value):
        value = slugify(value)
        if not value:
            raise serializers.ValidationError("A valid slug is required.")
        return value


from django.utils.text import slugify
from rest_framework import serializers
from .models import Membership, Organization

class OrganizationSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.id")

    class Meta:
        model = Organization
        fields = ["id", "name", "slug", "owner", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Organization name cannot be empty.")
        return value

    def validate_slug(self, value):
        value = slugify(value)
        if not value:
            raise serializers.ValidationError("A valid slug is required.")
        return value

class MembershipSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    organization = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Membership
        fields = ["id", "organization", "user", "role", "is_active", "joined_at"]
        read_only_fields = ["id", "organization", "user", "joined_at"]