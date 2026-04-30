from django.urls import path

from . import views

app_name = "solver"

urlpatterns = [
    path("solve/", views.SolveView.as_view(), name="solve"),
    path("standard-form/", views.StandardFormView.as_view(), name="standard_form"),
]
