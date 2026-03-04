from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.schemas import get_schema_view

from .schema import schema_view

urlpatterns = [
    path(
        "swagger(?<format>\\.json|\\.yaml)",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path(
        "api_schema",
        get_schema_view(title="API Schema", description="Guide for the REST API"),
        name="api_schema",
    ),
    path("admin/", admin.site.urls),
    path("how-it-works/", include("how_it_works.urls")),
    path("challenges/", include("challenges.urls")),
    path("surveys/", include("surveys.urls")),
    path("events/", include("events.urls")),
    path("prizes/", include("prizes.urls")),
    path("accounts/", include("accounts.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
