from django.urls import path

from . import views

app_name = "theory"

urlpatterns = [
    path("query/", views.TheoryQueryView.as_view(), name="query"),
]
