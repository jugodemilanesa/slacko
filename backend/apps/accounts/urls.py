from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    # Bootstrap de CSRF (setea la cookie csrftoken).
    path("csrf/", views.CSRFView.as_view(), name="csrf"),
    # Auth por sesión.
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("me/", views.MeView.as_view(), name="me"),
    # Login con Google (deja sesión de Django).
    path("google/", views.GoogleLogin.as_view(), name="google_login"),
]
