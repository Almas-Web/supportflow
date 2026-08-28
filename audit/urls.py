from django.urls import path
from .views import AuditLogListView, AuditLogDetailView

urlpatterns = [
    path("<int:organization_id>/audit-logs/", AuditLogListView.as_view(), name="audit-log-list"),
    path("<int:organization_id>/audit-logs/<int:pk>/", AuditLogDetailView.as_view(), name="audit-log-detail"),
]