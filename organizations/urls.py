from django.urls import path
from .views import MembershipDetailView, MembershipListCreateView, OrganizationDetailView, OrganizationListCreateView

urlpatterns = [
    path("", OrganizationListCreateView.as_view(), name="organization-list-create"),
    path("<int:pk>/", OrganizationDetailView.as_view(), name="organization-detail"),
    path("<int:organization_id>/members/", MembershipListCreateView.as_view(), name="membership-list-create"),
    path("<int:organization_id>/members/<int:pk>/", MembershipDetailView.as_view(), name="membership-detail"),
]