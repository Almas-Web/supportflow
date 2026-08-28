from django.urls import path
from .views import NotificationListView, NotificationDetailView, NotificationMarkReadView, NotificationMarkAllReadView

urlpatterns = [
    path("organizations/<int:organization_id>/notifications/", NotificationListView.as_view(), name="notification-list"),
    path("organizations/<int:organization_id>/notifications/<int:pk>/", NotificationDetailView.as_view(), name="notification-detail"),
    path("organizations/<int:organization_id>/notifications/<int:pk>/read/", NotificationMarkReadView.as_view(), name="notification-mark-read"),
    path("organizations/<int:organization_id>/notifications/mark-all-read/", NotificationMarkAllReadView.as_view(), name="notification-mark-all-read"),
]