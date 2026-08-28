from django.urls import path
from .views import ReportListCreateView, ReportDetailView

urlpatterns = [
    path("organizations/<int:organization_id>/reports/", ReportListCreateView.as_view(), name="report-list-create"),
    path("organizations/<int:organization_id>/reports/<int:pk>/", ReportDetailView.as_view(), name="report-detail"),
]