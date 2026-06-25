"""Main URL configuration."""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health(_request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/chat/", include("apps.chat.urls")),
    path("api/theory/", include("apps.theory.urls")),
    path("api/solver/", include("apps.solver.urls")),
    path("api/formulation/", include("apps.formulation.urls")),
    path("health/", health),
]
