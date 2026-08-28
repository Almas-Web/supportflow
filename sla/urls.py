from django.urls import path
from .views import SLAPolicyListCreateView, SLAPolicyDetailView, TicketSLAListCreateView, TicketSLADetailView
urlpatterns = [
    path("organizations/<int:organization_id>/sla-policies/", SLAPolicyListCreateView.as_view(), name="sla-policy-list-create"),
    path("organizations/<int:organization_id>/sla-policies/<int:pk>/", SLAPolicyDetailView.as_view(), name="sla-policy-detail"),
    path("organizations/<int:organization_id>/ticket-slas/", TicketSLAListCreateView.as_view(), name="ticket-sla-list-create"),
    path("organizations/<int:organization_id>/ticket-slas/<int:pk>/", TicketSLADetailView.as_view(), name="ticket-sla-detail"),
]