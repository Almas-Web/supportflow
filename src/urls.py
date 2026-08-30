from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/account/", include("account.urls")),
    path("api/organizations/", include("organizations.urls")),
    path("api/", include("teams.urls")),
    path("api/organizations/<int:organization_id>/customers/", include("customers.urls")),
    path("api/organizations/<int:organization_id>/tickets/", include("tickets.urls")),
    path("api/", include("sla.urls")),
    path("api/", include("notifications.urls")),
    path("api/organizations/", include("ratings.urls")),
    path("api/organizations/", include("audit.urls")),
    path("api/", include("analytics.urls")),
    path("api/", include("reports.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)