"""Main URL configuration."""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path, re_path

from apps.spa_view import SpaView


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
    # SPA catch-all: sirve archivos estáticos del frontend o index.html
    re_path(r"^(?P<path>.*)$", SpaView.as_view()),
]
