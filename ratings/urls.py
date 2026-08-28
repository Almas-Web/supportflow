from django.urls import path

from .views import RatingListCreateView, RatingDetailView


urlpatterns = [
    path("<int:organization_id>/ratings/", RatingListCreateView.as_view(), name="rating-list-create"),
    path("<int:organization_id>/ratings/<int:pk>/", RatingDetailView.as_view(), name="rating-detail"),
]