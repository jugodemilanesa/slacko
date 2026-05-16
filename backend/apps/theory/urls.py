from django.urls import path

from . import views

app_name = "theory"

urlpatterns = [
    path("categories/", views.CategoryListView.as_view(), name="categories"),
    path("concepts/", views.ConceptListView.as_view(), name="concepts"),
    path(
        "concepts/<slug:concept_id>/",
        views.ConceptDetailView.as_view(),
        name="concept_detail",
    ),
    path("query/", views.TheoryQueryView.as_view(), name="query"),
]
