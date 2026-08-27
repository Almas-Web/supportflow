from django.urls import path
from .views import TeamListCreateView, TeamDetailView, TeamMemberListCreateView, TeamMemberDetailView

urlpatterns = [
    path("organizations/<int:organization_id>/teams/", TeamListCreateView.as_view(), name="team-list-create"),
    path("organizations/<int:organization_id>/teams/<int:pk>/", TeamDetailView.as_view(), name="team-detail"),
    path("organizations/<int:organization_id>/teams/<int:team_id>/members/", TeamMemberListCreateView.as_view(), name="team-member-list-create"),
    path("organizations/<int:organization_id>/teams/<int:team_id>/members/<int:pk>/", TeamMemberDetailView.as_view(), name="team-member-detail"),
]