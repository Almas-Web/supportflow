from django.urls import path
from .views import AnalyticsSnapshotListCreateView, AnalyticsSnapshotDetailView, TicketAnalyticsView

urlpatterns = [
    path("organizations/<int:organization_id>/analytics/", AnalyticsSnapshotListCreateView.as_view(), name="analytics-list-create"),
    path("organizations/<int:organization_id>/analytics/summary/", TicketAnalyticsView.as_view(), name="analytics-summary"),
    path("organizations/<int:organization_id>/analytics/<int:pk>/", AnalyticsSnapshotDetailView.as_view(), name="analytics-detail"),
]