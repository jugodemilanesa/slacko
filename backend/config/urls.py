"""Main URL configuration."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/chat/", include("apps.chat.urls")),
    path("api/theory/", include("apps.theory.urls")),
    path("api/solver/", include("apps.solver.urls")),
    path("api/formulation/", include("apps.formulation.urls")),
]
