from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import serializers

from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "password", "role", "bio", "image"]
        extra_kwargs = {"password": {"write_only": True}, "image": {"required": False}}

    def create(self, validated_data):
        user = CustomUser(**validated_data)
        user.set_password(validated_data["password"])
        user.verification_token = get_random_string(length=32)
        user.save()
        self.send_email(user)
        return user

    def send_email(self, user):
        verification_link = self.context["request"].build_absolute_uri(reverse("verify_email", kwargs={"token": user.verification_token}))
        html_content = render_to_string("emails/verification_email.html", {"user": user.username, "verification_link": verification_link})
        email = EmailMultiAlternatives("Verify your email", "Please verify your email address.", "from@example.com", [user.email])
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        return True


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["bio", "image"]

    def update(self, instance, validated_data):
        instance.bio = validated_data.get("bio", instance.bio)
        instance.image = validated_data.get("image", instance.image)
        instance.save()
        return instance

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=8, write_only=True)