from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.crypto import get_random_string
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import EmptySerializer, PasswordResetConfirmSerializer, PasswordResetRequestSerializer, ResendVerificationEmailSerializer, UserLoginSerializer, UserSerializer, UserUpdateSerializer

@extend_schema(tags=["Account"])
class UserSignUp(generics.CreateAPIView):
    serializer_class = UserSerializer

@extend_schema(tags=["Account"])
class VerifyEmail(generics.GenericAPIView):
    serializer_class = EmptySerializer
    swagger_fake_view = True

    def get(self, request, token):
        user = CustomUser.objects.filter(verification_token=token).first()
        if user:
            if user.is_verified:
                return Response({"details": "Email already verified!"}, status=status.HTTP_400_BAD_REQUEST)
            user.is_verified = True
            user.verification_token = None
            user.save(update_fields=["is_verified", "verification_token"])
            return Response({"details": "Successfully verified!"}, status=status.HTTP_200_OK)
        return Response({"details": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=["Account"])
class ResendVerificationEmail(generics.GenericAPIView):
    serializer_class = ResendVerificationEmailSerializer
    swagger_fake_view = True

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        if not email:
            return Response({"details": "Email is required!"}, status=status.HTTP_400_BAD_REQUEST)
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            return Response({"details": "User with this email doesn't exist!"}, status=status.HTTP_404_NOT_FOUND)
        if user.is_verified:
            return Response({"details": "Email already verified!"}, status=status.HTTP_400_BAD_REQUEST)
        user.verification_token = get_random_string(length=32)
        user.save(update_fields=["verification_token"])
        verification_link = request.build_absolute_uri(reverse("verify_email", kwargs={"token": user.verification_token}))
        html_content = render_to_string("emails/verification_email.html", {"user": user.username, "verification_link": verification_link})
        email_message = EmailMultiAlternatives("Verify your email", "Please verify your email address.", "from@example.com", [user.email])
        email_message.attach_alternative(html_content, "text/html")
        email_message.send(fail_silently=False)
        return Response({"details": "Verification email sent!"}, status=status.HTTP_200_OK)

@extend_schema(tags=["Account"])
class UserLogin(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        user = CustomUser.objects.filter(email=email).first()
        if user and user.check_password(password):
            if not user.is_verified:
                return Response({"details": "Email is not verified yet!"}, status=status.HTTP_401_UNAUTHORIZED)
            refresh = RefreshToken.for_user(user)
            return Response({"refresh_token": str(refresh), "access_token": str(refresh.access_token)})
        return Response({"details": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

@extend_schema(tags=["Account"])
class RetrieveUpdateProfile(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return UserUpdateSerializer
        return UserSerializer

@extend_schema(tags=["Account"])
class PasswordResetRequest(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer

    @extend_schema(operation_id="password_reset_request")
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            return Response({"details": "User with this email doesn't exist!"}, status=status.HTTP_404_NOT_FOUND)
        token = default_token_generator.make_token(user)
        return Response({"details": "Password reset token generated!", "token": token}, status=status.HTTP_200_OK)

@extend_schema(tags=["Account"])
class PasswordResetConfirm(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer

    @extend_schema(operation_id="password_reset_confirm")
    def post(self, request, uid, token):
        user = CustomUser.objects.filter(id=uid).first()
        if not user or not default_token_generator.check_token(user, token):
            return Response({"details": "Invalid or expired token!"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])
        return Response({"details": "Password reset successfully!"}, status=status.HTTP_200_OK)

@extend_schema(tags=["Account"])
class ActivateDeactivateUser(generics.GenericAPIView):
    serializer_class = EmptySerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])
        return Response({"details": "User activated!" if user.is_active else "User deactivated!", "is_active": user.is_active}, status=status.HTTP_200_OK)
    