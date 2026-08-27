from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import ActivateDeactivateUser, PasswordResetConfirm, PasswordResetRequest, ResendVerificationEmail, RetrieveUpdateProfile, UserLogin, UserSignUp, VerifyEmail

urlpatterns = [
    path("signup/", UserSignUp.as_view(), name="signup"),
    path("verify-email/<str:token>/", VerifyEmail.as_view(), name="verify_email"),
    path("resend-verification/", ResendVerificationEmail.as_view(), name="resend_verification"),
    path("login/", UserLogin.as_view(), name="login"),
    path("profile/", RetrieveUpdateProfile.as_view(), name="profile"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("password-reset/", PasswordResetRequest.as_view(), name="password_reset"),
    path("password-reset/<int:uid>/<str:token>/", PasswordResetConfirm.as_view(), name="password_reset_confirm"),
    path("activate-deactivate/", ActivateDeactivateUser.as_view(), name="activate_deactivate"),
]