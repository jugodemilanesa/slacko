from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

app_name = "accounts"

urlpatterns = [
    # Legacy endpoints (kept for backward compat with the current frontend).
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", views.MeView.as_view(), name="me"),
    # Logout explícito que blacklistea el refresh. Va ANTES del include de
    # dj-rest-auth para tener prioridad sobre su /logout/ genérico.
    path("logout/", views.LogoutView.as_view(), name="logout"),
    # dj-rest-auth full surface: password reset, change, user details, logout.
    path("", include("dj_rest_auth.urls")),
    # dj-rest-auth registration (extra endpoints beyond legacy register/).
    path("registration/", include("dj_rest_auth.registration.urls")),
    # Social login.
    path("google/", views.GoogleLogin.as_view(), name="google_login"),
]
